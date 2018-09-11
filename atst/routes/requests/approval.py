from flask import (
    render_template,
    g,
    Response,
    request as http_request,
    redirect,
    url_for,
)
from flask import current_app as app

from . import requests_bp
from atst.domain.requests import Requests
from atst.domain.exceptions import NotFoundError
from atst.forms.ccpo_review import CCPOReviewForm


def task_order_dictionary(task_order):
    return {
        c.name: getattr(task_order, c.name)
        for c in task_order.__table__.columns
        if c.name not in ["id", "attachment_id"]
    }


def render_approval(request, form=None):
    data = request.body
    pending_final_approval = Requests.is_pending_ccpo_approval(request)
    pending_review = (
        Requests.is_pending_ccpo_acceptance(request) or pending_final_approval
    )
    if pending_final_approval and request.task_order:
        data["task_order"] = task_order_dictionary(request.task_order)

    return render_template(
        "requests/approval.html",
        data=data,
        request_id=request.id,
        status=request.status.value,
        pending_review=pending_review,
        financial_review=pending_final_approval,
        pdf_available=request.task_order and request.task_order.pdf,
        f=form or CCPOReviewForm(),
    )


@requests_bp.route("/requests/approval/<string:request_id>", methods=["GET"])
def approval(request_id):
    request = Requests.get_for_approval(g.current_user, request_id)

    return render_approval(request)


@requests_bp.route("/requests/submit_approval/<string:request_id>", methods=["POST"])
def submit_approval(request_id):
    request = Requests.get_for_approval(g.current_user, request_id)

    form = CCPOReviewForm(http_request.form)
    if form.validate():
        if http_request.form.get("approved"):
            Requests.advance(g.current_user, request, form.data)
        else:
            Requests.request_changes(g.current_user, request, form.data)

        return redirect(url_for("requests.requests_index"))
    else:
        return render_approval(request, form)


@requests_bp.route("/requests/task_order_download/<string:request_id>", methods=["GET"])
def task_order_pdf_download(request_id):
    request = Requests.get(g.current_user, request_id)
    if request.task_order and request.task_order.pdf:
        pdf = request.task_order.pdf
        generator = app.uploader.download_stream(pdf.object_name)
        return Response(
            generator,
            headers={
                "Content-Disposition": "attachment; filename={}".format(pdf.filename)
            },
            mimetype="application/pdf",
        )

    else:
        raise NotFoundError("task_order pdf")
