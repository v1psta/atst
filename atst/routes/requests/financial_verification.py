from flask import g, render_template, redirect, url_for
from flask import request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm


class FinancialVerification:
    def __init__(self, user, request_id=None, extended=False, post_data=None):
        self.request = Requests.get(user, request_id)
        self._extended = extended
        self.post_data = post_data
        self._form = None
        self.reset()

    def reset(self):
        self.updateable = False
        self.valid = False
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
        if self.post_data:
            return self.post_data
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
            self.updateable = True
            self.valid = self.form.perform_extra_validation(
                self.request.body.get("financial_verification")
            )
        else:
            self.updateable = False
            self.valid = False

        return self.valid

    @property
    def pending(self):
        return self.request.is_pending_ccpo_approval

    def finalize(self):
        if self.updateable:
            self.request = Requests.update_financial_verification(
                self.request.id, self.form.data
            )

        if self.valid:
            self.request = Requests.submit_financial_verification(self.request)

            if self.request.is_financially_verified:
                self.workspace = Requests.approve_and_create_workspace(self.request)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    finver = FinancialVerification(
        g.current_user,
        request_id=request_id,
        extended=http_request.args.get("extended"),
    )

    return render_template(
        "requests/financial_verification.html",
        f=finver.form,
        jedi_request=finver.request,
        review_comment=finver.request.review_comment,
        extended=finver.is_extended,
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification(request_id):
    finver = FinancialVerification(
        g.current_user,
        request_id=request_id,
        extended=http_request.args.get("extended"),
        post_data=http_request.form,
    )

    finver.validate()

    finver.finalize()

    if finver.workspace:
        return redirect(
            url_for(
                "workspaces.new_project",
                workspace_id=finver.workspace.id,
                newWorkspace=True,
            )
        )
    elif finver.pending:
        return redirect(url_for("requests.requests_index", modal="pendingCCPOApproval"))
    else:
        finver.reset()
        return render_template(
            "requests/financial_verification.html",
            jedi_request=finver.request,
            f=finver.form,
            extended=finver.is_extended,
        )
