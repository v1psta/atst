from flask import g, render_template, redirect, url_for
from flask import request as http_request
from werkzeug.datastructures import ImmutableMultiDict

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm
from atst.forms.exceptions import FormValidationError
from atst.domain.requests.financial_verification import (
    PENumberValidator,
    TaskOrderNumberValidator,
)


class FinancialVerificationBase(object):
    def _get_form(self, request, is_extended, input_data):
        data = input_data

        fv_data = request.body.get("financial_verification", {})
        data = {**data, **fv_data}

        if request.task_order:
            task_order_dict = request.task_order.to_dictionary()
            task_order_dict.update(
                {
                    "task_order_number": request.task_order.number,
                    "funding_type": request.task_order.funding_type.value,
                }
            )
            data = {**data, **task_order_dict}

        mdict = ImmutableMultiDict(data)
        if is_extended:
            return ExtendedFinancialForm(formdata=mdict)
        else:
            return FinancialForm(formdata=mdict)

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


class GetFinancialVerificationForm(FinancialVerificationBase):
    def __init__(self, user, request, is_extended=False):
        self.user = user
        self.request = request
        self.is_extended = is_extended

    def execute(self):
        form = self._get_form(self.request, self.is_extended, {})
        return {"form": form}


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
        submitted = False
        workspace = None

        if not form.validate():
            should_update = False

        if not self.pe_validator.validate(self.request, form.pe_id.data):
            self._apply_pe_number_error(form.pe_id)
            should_submit = False

        if not self.task_order_validator.validate(form.task_order_number.data):
            self._apply_task_order_number_error(form.task_order_number)
            should_submit = False

        if should_update:
            updated_request = Requests.update_financial_verification(
                self.request.id, form.data
            )
        else:
            form.reset()
            raise FormValidationError(form)

        if should_submit:
            updated_request = Requests.submit_financial_verification(updated_request)
            if updated_request.is_financially_verified:
                workspace = Requests.approve_and_create_workspace(updated_request)
                submitted = True
        else:
            form.reset()
            raise FormValidationError(form)

        if submitted:
            return {
                "state": "submitted",
                "workspace": workspace,
                "request": updated_request,
            }
        else:
            return {"state": "pending", "request": updated_request}


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
            valid = False

        if (
            valid
            and form.pe_id.data
            and not self.pe_validator.validate(self.request, form.pe_id.data)
        ):
            self._apply_pe_number_error(form.pe_id)
            valid = False

        if (
            valid
            and form.task_order_number.data
            and not self.task_order_validator.validate(form.task_order_number.data)
        ):
            self._apply_task_order_number_error(form.task_order_number)
            valid = False

        if not valid:
            form.reset()
            raise FormValidationError(form)
        else:
            updated_request = Requests.update_financial_verification(
                self.request.id, form.data
            )
            return {"request": updated_request}


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    is_extended = http_request.args.get("extended")

    response_context = GetFinancialVerificationForm(
        g.current_user, request, is_extended=is_extended
    ).execute()

    return render_template(
        "requests/financial_verification.html",
        f=response_context["form"],
        jedi_request=request,
        review_comment=request.review_comment,
        extended=is_extended,
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    fv_data = http_request.form
    is_extended = http_request.args.get("extended")

    try:
        response_context = UpdateFinancialVerification(
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

    if response_context["state"] == "submitted":
        workspace = response_context["workspace"]
        return redirect(
            url_for(
                "workspaces.new_project", workspace_id=workspace.id, newWorkspace=True
            )
        )
    elif response_context["state"] == "pending":
        return redirect(url_for("requests.requests_index", modal="pendingCCPOApproval"))


@requests_bp.route("/requests/verify/<string:request_id>/draft", methods=["POST"])
def save_financial_verification_draft(request_id):
    request = Requests.get(g.current_user, request_id)
    fv_data = http_request.form
    is_extended = http_request.args.get("extended")

    try:
        response_context = SaveFinancialVerificationDraft(
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
