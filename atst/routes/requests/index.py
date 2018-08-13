import pendulum
from flask import render_template, g, url_for

from . import requests_bp
from atst.domain.requests import Requests


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
    if "review_and_approve_jedi_workspace_request" in g.current_user.atat_permissions:
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator=g.current_user)

    mapped_requests = [map_request(r) for r in requests]

    pending_fv_count = [
        True for r in requests if Requests.is_pending_financial_verification(r)
    ]
    pending_fv = len(pending_fv_count) > 1
    pending_ccpo = len(pending_fv_count) != len(mapped_requests)

    return render_template(
        "requests.html",
        requests=mapped_requests,
        pending_financial_verification=pending_fv,
        pending_ccpo_approval=pending_ccpo,
    )
