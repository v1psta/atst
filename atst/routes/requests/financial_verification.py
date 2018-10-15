from flask import g, render_template, redirect, url_for
from flask import request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm
from atst.forms.exceptions import FormValidationError
from atst.domain.requests.financial_verification import (
    PENumberValidator,
    TaskOrderNumberValidator,
)


class FinancialVerification:
    def __init__(self, request, extended=False, post_data=None):
        self.request = request
        self._extended = extended
        self._post_data = post_data
        self._form = None
        self.reset()

    def reset(self):
        self._updateable = False
        self._valid = False
        self.workspace = None
        if self._form:
            self._form.reset()

    @property
    def is_extended(self):
        return self._extended or self.is_pending_changes

    @property
    def is_pending_changes(self):
        return self.request.is_pending_financial_verification_changes

    @property
    def _task_order_data(self):
        if self.request.task_order:
            task_order = self.request.task_order
            data = task_order.to_dictionary()
            data["task_order_number"] = task_order.number
            data["funding_type"] = task_order.funding_type.value
            return data
        else:
            return {}

    @property
    def _form_data(self):
        if self._post_data:
            return self._post_data
        else:
            form_data = self.request.body.get("financial_verification", {})
            form_data.update(self._task_order_data)

            return form_data

    @property
    def form(self):
        if not self._form:
            if self.is_extended:
                self._form = ExtendedFinancialForm(data=self._form_data)
            else:
                self._form = FinancialForm(data=self._form_data)

        return self._form

    def validate(self):
        if self.form.validate():
            self._updateable = True
            self._valid = self.form.perform_extra_validation(
                self.request.body.get("financial_verification")
            )
        else:
            self._updateable = False
            self._valid = False

        return self._valid

    @property
    def pending(self):
        return self.request.is_pending_ccpo_approval

    def finalize(self):
        if self._updateable:
            self.request = Requests.update_financial_verification(
                self.request.id, self.form.data
            )

        if self._valid:
            self.request = Requests.submit_financial_verification(self.request)

            if self.request.is_financially_verified:
                self.workspace = Requests.approve_and_create_workspace(self.request)


class UpdateFinancialVerification(object):
    def __init__(
        self, pe_validator, task_order_validator, request, fv_data, is_extended=False
    ):
        self.pe_validator = pe_validator
        self.task_order_validator = task_order_validator
        self.request = request
        self.fv_data = fv_data
        self.is_extended = is_extended

    def execute(self):
        fv = FinancialVerification(self.request, self.is_extended, self.fv_data)

        should_update = True
        should_submit = True

        if not fv.validate():
            should_update = False

        if not self.pe_validator.validate(self.request, fv.form.pe_id):
            suggestion = self.pe_validator.suggest_pe_id(fv.form.pe_id.data)
            error_str = (
                "We couldn't find that PE number. {}"
                "If you have double checked it you can submit anyway. "
                "Your request will need to go through a manual review."
            ).format('Did you mean "{}"? '.format(suggestion) if suggestion else "")
            fv.form.pe_id.errors += (error_str,)
            should_submit = False

        if not self.task_order_validator.validate(fv.form.task_order_number):
            fv.form.task_order_number.errors += ("Task Order number not found",)
            should_submit = False

        if should_update:
            Requests.update_financial_verification(self.request.id, fv.form.data)
        else:
            fv.form.reset()
            raise FormValidationError(fv.form)

        if should_submit:
            submitted_request = Requests.submit_financial_verification(self.request)
            if submitted_request.is_financially_verified:
                workspace = Requests.approve_and_create_workspace(submitted_request)
                return {"state": "submitted", "workspace": workspace}
            else:
                return {"state": "pending"}
        else:
            fv.form.reset()
            raise FormValidationError(fv.form)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    request = Requests.get(g.current_user, request_id)
    finver = FinancialVerification(request, extended=http_request.args.get("extended"))

    return render_template(
        "requests/financial_verification.html",
        f=finver.form,
        jedi_request=finver.request,
        review_comment=finver.request.review_comment,
        extended=finver.is_extended,
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
