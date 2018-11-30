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
from atst.utils.flash import formatted_flash as flash


def map_ccpo_authorizing(user):
    return {"fname_ccpo": user.first_name, "lname_ccpo": user.last_name}


def render_approval(request, form=None, internal_comment_form=None):
    data = request.body
    if request.has_financial_data:
        data["task_order"] = request.task_order.to_dictionary()

    if not form:
        mo_data = map_ccpo_authorizing(g.current_user)
        form = CCPOReviewForm(data=mo_data)

    if not internal_comment_form:
        internal_comment_form = InternalCommentForm()

    return render_template(
        "requests/approval.html",
        data=data,
        reviews=list(reversed(request.reviews)),
        jedi_request=request,
        current_status=request.status.value,
        review_form=form or CCPOReviewForm(),
        internal_comment_form=internal_comment_form,
        comments=request.internal_comments,
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
        if http_request.form.get("review") == "approving":
            Requests.advance(g.current_user, request, form.data)
        else:
            Requests.request_changes(g.current_user, request, form.data)

        return redirect(url_for("requests.requests_index"))
    else:
        flash("form_errors")
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
    request = Requests.get(g.current_user, request_id)
    if form.validate():
        Requests.add_internal_comment(g.current_user, request, form.data.get("text"))
        return redirect(
            url_for("requests.approval", request_id=request_id, _anchor="ccpo-notes")
        )
    else:
        flash("form_errors")
        return render_approval(request, internal_comment_form=form)
