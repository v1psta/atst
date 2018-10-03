from flask import g, render_template, redirect, url_for
from flask import request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm


def task_order_data(task_order):
    data = task_order.to_dictionary()
    data["task_order_number"] = task_order.number
    data["funding_type"] = task_order.funding_type.value
    return data


def is_extended(request):
    return (
        http_request.args.get("extended")
        or request.is_pending_financial_verification_changes
    )


def financial_form(request, data):
    if is_extended(request):
        return ExtendedFinancialForm(data=data)
    else:
        return FinancialForm(data=data)


class FinancialVerification:
    def __init__(self, user, request_id=None, extended=False, post_data=None):
        self.request = Requests.get(user, request_id)
        self._extended = extended
        self.post_data = post_data

    @property
    def is_extended(self):
        return self._extended or self.is_pending_changes

    @property
    def is_pending_changes(self):
        return self.request.is_pending_financial_verification_changes

    @property
    def _task_order_data(self):
        if self.request.task_order:
            data = self.request.task_order.to_dictionary()
            data["task_order_number"] = task_order.number
            data["funding_type"] = task_order.funding_type.value
            return data
        else:
            return {}

    @property
    def _form_data(self):
        form_data = self.request.body.get("financial_verification", {})
        form_data.update(self._task_order_data)

        return form_data

    @property
    def form(self):
        if self.is_extended:
            return ExtendedFinancialForm(self._form_data)
        else:
            return FinancialForm(self._form_data)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id):
    finver = FinancialVerification(
        g.current_user, request_id=request_id, extended=http_request.args.get("extended")
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
    post_data = http_request.form
    existing_request = Requests.get(g.current_user, request_id)
    form = financial_form(existing_request, post_data)
    rerender_args = dict(
        jedi_request=existing_request, f=form, extended=is_extended(existing_request)
    )

    if form.validate():
        valid = form.perform_extra_validation(
            existing_request.body.get("financial_verification")
        )
        updated_request = Requests.update_financial_verification(request_id, form.data)
        if valid:
            submitted_request = Requests.submit_financial_verification(updated_request)
            if submitted_request.is_financially_verified:
                new_workspace = Requests.approve_and_create_workspace(submitted_request)
                return redirect(
                    url_for(
                        "workspaces.new_project",
                        workspace_id=new_workspace.id,
                        newWorkspace=True,
                    )
                )
            else:
                return redirect(
                    url_for("requests.requests_index", modal="pendingCCPOApproval")
                )

        else:
            form.reset()
            return render_template(
                "requests/financial_verification.html", **rerender_args
            )

    else:
        form.reset()
        return render_template("requests/financial_verification.html", **rerender_args)
