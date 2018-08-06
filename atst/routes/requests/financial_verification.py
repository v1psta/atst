from flask import render_template, redirect, url_for
from flask import request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm
from atst.domain.auth import login_required


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
@login_required
def financial_verification(request_id=None):
    request = Requests.get(request_id)
    form = FinancialForm(data=request.body.get("financial_verification"))
    return render_template(
        "requests/financial_verification.html", f=form, request_id=request_id
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
@login_required
def update_financial_verification(request_id):
    post_data = http_request.form
    existing_request = Requests.get(request_id)
    form = FinancialForm(post_data)

    rerender_args = dict(request_id=request_id, f=form)

    if form.validate():
        request_data = {"financial_verification": post_data}
        Requests.update(request_id, request_data)
        valid = form.perform_extra_validation(
            existing_request.body.get("financial_verification")
        )
        if valid:
            return redirect(url_for("requests.financial_verification_submitted"))
        else:
            return render_template(
                "requests/financial_verification.html", **rerender_args
            )
    else:
        return render_template("requests/financial_verification.html", **rerender_args)


@requests_bp.route("/requests/financial_verification_submitted")
@login_required
def financial_verification_submitted():
    pass
