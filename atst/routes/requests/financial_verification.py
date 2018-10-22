from flask import g, render_template, redirect, url_for
from flask import request as http_request
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm
from atst.forms.exceptions import FormValidationError
from atst.domain.exceptions import NotFoundError
from atst.domain.requests.financial_verification import (
    PENumberValidator,
    TaskOrderNumberValidator,
)
from atst.models.attachment import Attachment
from atst.domain.task_orders import TaskOrders
from atst.utils import getattr_path


def fv_extended(_http_request):
    return _http_request.args.get("extended", "false").lower() in ["true", "t"]


class FinancialVerificationBase(object):
    def _get_form(self, request, is_extended, formdata=None):
        existing_fv_data = request.financial_verification

        if request.task_order:
            task_order_dict = request.task_order.to_dictionary()
            task_order_dict.update(
                {
                    "task_order_number": request.task_order.number,
                    "funding_type": getattr_path(
                        request, "task_order.funding_type.value"
                    ),
                }
            )
            existing_fv_data = {**existing_fv_data, **task_order_dict}

        mdict = ImmutableMultiDict(formdata) if formdata is not None else None
        if is_extended:
            try:
                attachment = Attachment.get_for_resource("task_order", self.request.id)
                existing_fv_data["task_order"] = attachment.filename
            except NotFoundError:
                pass

            return ExtendedFinancialForm(formdata=mdict, data=existing_fv_data)
        else:
            return FinancialForm(formdata=mdict, data=existing_fv_data)

    def _process_attachment(self, is_extended, form):
        attachment = None
        if is_extended:
            attachment = None
            if isinstance(form.task_order.data, FileStorage):
                Attachment.delete_for_resource("task_order", self.request.id)
                attachment = Attachment.attach(
                    form.task_order.data, "task_order", self.request.id
                )
            elif isinstance(form.task_order.data, str):
                try:
                    attachment = Attachment.get_for_resource(
                        "task_order", self.request.id
                    )
                except NotFoundError:
                    pass

            if attachment:
                form.task_order.data = attachment.filename

        return attachment

    def _try_create_task_order(self, form, attachment):
        form_data = form.data

        task_order_number = form_data.get("task_order_number")
        if task_order_number:
            task_order_data = {
                k: v for (k, v) in form_data.items() if k in TaskOrders.TASK_ORDER_DATA
            }
            return TaskOrders.get_or_create(
                task_order_number, attachment=attachment, data=task_order_data
            )
        return None

    def _apply_pe_number_error(self, field):
        suggestion = self.pe_validator.suggest_pe_id(field.data)
        error_str = (
            "We couldn't find that PE number. {}"
            "If you have double checked it you can submit anyway. "
            "Your request will need to go through a manual review."
        ).format('Did you mean "{}"? '.format(suggestion) if suggestion else "")
        field.errors += (error_str,)

    def _apply_task_order_number_error(self, field):
        field.errors += ("Task Order number not found",)

    def _raise(self, form):
        form.reset()
        raise FormValidationError(form)


class GetFinancialVerificationForm(FinancialVerificationBase):
    def __init__(self, user, request, is_extended=False):
        self.user = user
        self.request = request
        self.is_extended = is_extended

    def execute(self):
        form = self._get_form(self.request, self.is_extended)
        return form


class UpdateFinancialVerification(FinancialVerificationBase):
    def __init__(
        self,
        pe_validator,
        task_order_validator,
        user,
        request,
        fv_data,
        is_extended=False,
    ):
        self.pe_validator = pe_validator
        self.task_order_validator = task_order_validator
        self.user = user
        self.request = request
        self.fv_data = fv_data
        self.is_extended = is_extended

    def execute(self):
        form = self._get_form(self.request, self.is_extended, self.fv_data)

        should_update = True
        should_submit = True
        updated_request = None

        if not form.validate():
            should_update = False

        if not self.pe_validator.validate(self.request, form.pe_id.data):
            self._apply_pe_number_error(form.pe_id)
            should_submit = False

        if not self.task_order_validator.validate(form.task_order_number.data):
            self._apply_task_order_number_error(form.task_order_number)
            should_submit = False

        attachment = self._process_attachment(self.is_extended, form)

        if should_update:
            task_order = self._try_create_task_order(form, attachment)
            updated_request = Requests.update_financial_verification(
                self.request.id, form.data, task_order=task_order
            )
            if should_submit:
                return Requests.submit_financial_verification(updated_request)

        self._raise(form)


class SaveFinancialVerificationDraft(FinancialVerificationBase):
    def __init__(
        self,
        pe_validator,
        task_order_validator,
        user,
        request,
        fv_data,
        is_extended=False,
    ):
        self.pe_validator = pe_validator
        self.task_order_validator = task_order_validator
        self.user = user
        self.request = request
        self.fv_data = fv_data
        self.is_extended = is_extended

    def execute(self):
        form = self._get_form(self.request, self.is_extended, self.fv_data)
        valid = True

        if not form.validate_draft():
            self._raise(form)

        if form.pe_id.data and not self.pe_validator.validate(
            self.request, form.pe_id.data
        ):
            valid = False
            self._apply_pe_number_error(form.pe_id)

        if form.task_order_number.data and not self.task_order_validator.validate(
            form.task_order_number.data
        ):
            valid = False
            self._apply_task_order_number_error(form.task_order_number)

        attachment = self._process_attachment(self.is_extended, form)
        task_order = self._try_create_task_order(form, attachment)
        updated_request = Requests.update_financial_verification(
            self.request.id, form.data, task_order=task_order
        )

        if valid:
            return updated_request
        else:
            self._raise(form)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    is_extended = fv_extended(http_request)

    should_be_extended = not is_extended and request.has_manual_task_order
    if should_be_extended:
        return redirect(
            url_for(".financial_verification", request_id=request_id, extended=True)
        )

    form = GetFinancialVerificationForm(
        g.current_user, request, is_extended=is_extended
    ).execute()

    return render_template(
        "requests/financial_verification.html",
        f=form,
        jedi_request=request,
        review_comment=request.review_comment,
        extended=is_extended,
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    fv_data = {**http_request.form, **http_request.files}
    is_extended = fv_extended(http_request)

    try:
        updated_request = UpdateFinancialVerification(
            PENumberValidator(),
            TaskOrderNumberValidator(),
            g.current_user,
            request,
            fv_data,
            is_extended=is_extended,
        ).execute()
    except FormValidationError as e:
        return render_template(
            "requests/financial_verification.html",
            jedi_request=request,
            f=e.form,
            extended=is_extended,
        )

    if updated_request.is_pending_ccpo_approval:
        workspace = Requests.approve_and_create_workspace(updated_request)
        return redirect(
            url_for(
                "workspaces.new_project", workspace_id=workspace.id, newWorkspace=True
            )
        )
    else:
        return redirect(url_for("requests.requests_index", modal="pendingCCPOApproval"))


@requests_bp.route("/requests/verify/<string:request_id>/draft", methods=["POST"])
def save_financial_verification_draft(request_id):
    request = Requests.get(g.current_user, request_id)
    fv_data = {**http_request.form, **http_request.files}
    is_extended = fv_extended(http_request)

    try:
        SaveFinancialVerificationDraft(
            PENumberValidator(),
            TaskOrderNumberValidator(),
            g.current_user,
            request,
            fv_data,
            is_extended=is_extended,
        ).execute()
    except FormValidationError as e:
        return render_template(
            "requests/financial_verification.html",
            jedi_request=request,
            f=e.form,
            extended=is_extended,
        )

    return redirect(url_for("requests.requests_index"))
