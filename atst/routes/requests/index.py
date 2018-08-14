import pendulum
from flask import render_template, g, url_for

from . import requests_bp
from atst.domain.requests import Requests
from atst.models.permissions import Permissions


def map_request(request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()
    app_count = request.body.get("details_of_use", {}).get("num_software_systems", 0)
    update_url = url_for(
        "requests.requests_form_update", screen=1, request_id=request.id
    )
    verify_url = url_for("requests.financial_verification", request_id=request.id)

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status_displayname,
        "app_count": app_count,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": request.creator.full_name,
        "edit_link": verify_url if Requests.is_pending_financial_verification(
            request
        ) else update_url,
    }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    requests = []
    is_ccpo = Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST in g.current_user.atat_permissions
    if is_ccpo:
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator=g.current_user)

    mapped_requests = [map_request(r) for r in requests]

    pending_fv = not is_ccpo and any(Requests.is_pending_financial_verification(r) for r in requests)
    pending_ccpo = not is_ccpo and any(Requests.is_pending_ccpo_approval(r) for r in requests)

    return render_template(
        "requests.html",
        requests=mapped_requests,
        pending_financial_verification=pending_fv,
        pending_ccpo_approval=pending_ccpo,
    )
