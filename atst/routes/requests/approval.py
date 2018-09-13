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
from atst.forms.internal_comment import InternalCommentForm


def map_ccpo_authorizing(user):
    return {"fname_ccpo": user.first_name, "lname_ccpo": user.last_name}


def render_approval(request, form=None):
    data = request.body
    pending_final_approval = request.is_pending_ccpo_approval
    pending_review = request.is_pending_ccpo_acceptance or pending_final_approval
    if pending_final_approval and request.task_order:
        data["task_order"] = request.task_order.to_dictionary()

    internal_comment_form = InternalCommentForm(text=request.internal_comments_text)

    if not form:
        mo_data = map_ccpo_authorizing(g.current_user)
        form = CCPOReviewForm(data=mo_data)

    return render_template(
        "requests/approval.html",
        data=data,
        reviews=list(reversed(request.reviews)),
        request=request,
        current_status=request.status.value,
        pending_review=pending_review,
        financial_review=pending_final_approval,
        f=form or CCPOReviewForm(),
        internal_comment_form=internal_comment_form,
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


@requests_bp.route("/requests/internal_comments/<string:request_id>", methods=["POST"])
def create_internal_comment(request_id):
    form = InternalCommentForm(http_request.form)
    if form.validate():
        request = Requests.get(g.current_user, request_id)
        Requests.update_internal_comments(g.current_user, request, form.data["text"])

    return redirect(url_for("requests.approval", request_id=request_id))
