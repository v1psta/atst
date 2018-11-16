from flask import g, render_template, redirect, url_for, current_app as app
from flask import request as http_request
from werkzeug.datastructures import ImmutableMultiDict, FileStorage

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialVerificationForm
from atst.forms.exceptions import FormValidationError
from atst.domain.exceptions import NotFoundError
from atst.domain.requests.financial_verification import (
    PENumberValidator,
    TaskOrderNumberValidator,
)
from atst.models.attachment import Attachment
from atst.domain.task_orders import TaskOrders


def fv_extended(_http_request):
    return _http_request.args.get("extended", "false").lower() in ["true", "t"]


class FinancialVerification(object):
    def __init__(self, request):
        self.request = request.latest_revision
        self.task_order = request.task_order


class FinancialVerificationBase(object):
    def _get_form(self, request, is_extended, formdata=None):
        _formdata = ImmutableMultiDict(formdata) if formdata is not None else None
        fv = FinancialVerification(request)
        form = FinancialVerificationForm(obj=fv, formdata=_formdata)

        if not form.has_task_order_pdf:
            try:
                attachment = Attachment.get_for_resource("task_order", self.request.id)
                form.task_order.pdf.data = attachment.filename
            except NotFoundError:
                pass

        return form

    def _process_attachment(self, is_extended, form):
        attachment = None
        if is_extended:
            attachment = None
            if isinstance(form.task_order.pdf.data, FileStorage):
                Attachment.delete_for_resource("task_order", self.request.id)
                attachment = Attachment.attach(
                    form.task_order.pdf.data, "task_order", self.request.id
                )
            elif isinstance(form.task_order.pdf.data, str):
                try:
                    attachment = Attachment.get_for_resource(
                        "task_order", self.request.id
                    )
                except NotFoundError:
                    pass

            if attachment:
                form.task_order.pdf.data = attachment.filename

        return attachment

    def _try_create_task_order(self, form, attachment, is_extended):
        task_order_number = form.task_order.number.data
        if not task_order_number:
            return None

        task_order_data = form.task_order.data

        if attachment:
            task_order_data["pdf"] = attachment

        try:
            task_order = TaskOrders.get(task_order_number)
            task_order = TaskOrders.update(task_order, task_order_data)
            return task_order
        except NotFoundError:
            pass

        try:
            return TaskOrders.get_from_eda(task_order_number)
        except NotFoundError:
            pass

        return TaskOrders.create(**task_order_data)

    def _raise(self, form):
        form.reset()
        raise FormValidationError(form)


class GetFinancialVerificationForm(FinancialVerificationBase):
    def __init__(self, user, request, cached_data=None, is_extended=False):
        self.user = user
        self.request = request
        self.cached_data = cached_data or {}
        self.is_extended = is_extended

    def execute(self):
        form = self._get_form(self.request, self.is_extended, formdata=self.cached_data)
        form.reset()
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

        attachment = self._process_attachment(self.is_extended, form)

        if not form.validate(is_extended=self.is_extended, has_attachment=attachment):
            should_update = False

        if not self.pe_validator.validate(self.request, form.pe_id):
            should_submit = False

        if not self.is_extended and not self.task_order_validator.validate(
            form.task_order.number
        ):
            should_submit = False

        if should_update:
            task_order = self._try_create_task_order(form, attachment, self.is_extended)
            updated_request = Requests.update_financial_verification(
                self.request.id, form.request.data, task_order=task_order
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
        attachment = self._process_attachment(self.is_extended, form)
        task_order = self._try_create_task_order(form, attachment, self.is_extended)
        updated_request = Requests.update_financial_verification(
            self.request.id, form.request.data, task_order=task_order
        )

        return updated_request


@requests_bp.route("/requests/verify/<string:request_id>/draft", methods=["GET"])
@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    is_extended = fv_extended(http_request)
    saved_draft = http_request.args.get("saved_draft", False)

    should_be_extended = not is_extended and request.has_manual_task_order
    if should_be_extended:
        return redirect(
            url_for(".financial_verification", request_id=request_id, extended=True)
        )

    form = GetFinancialVerificationForm(
        g.current_user,
        request,
        is_extended=is_extended,
        cached_data=app.form_cache.from_request(http_request),
    ).execute()

    return render_template(
        "requests/financial_verification.html",
        f=form,
        jedi_request=request,
        review_comment=request.review_comment,
        extended=is_extended,
        saved_draft=saved_draft,
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

    if updated_request.task_order.verified:
        workspace = Requests.auto_approve_and_create_workspace(updated_request)
        return redirect(
            url_for(
                "workspaces.new_project", workspace_id=workspace.id, newWorkspace=True
            )
        )
    else:
        return redirect(url_for("requests.requests_index", modal="pendingCCPOApproval"))


@requests_bp.route("/requests/verify/<string:request_id>/draft", methods=["POST"])
def save_financial_verification_draft(request_id):
    user = g.current_user
    request = Requests.get(user, request_id)
    fv_data = {**http_request.form, **http_request.files}
    is_extended = fv_extended(http_request)

    try:
        updated_request = SaveFinancialVerificationDraft(
            PENumberValidator(),
            TaskOrderNumberValidator(),
            user,
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

    return redirect(
        url_for(
            "requests.financial_verification",
            request_id=updated_request.id,
            is_extended=is_extended,
            saved_draft=True,
        )
    )
