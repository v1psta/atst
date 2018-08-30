import pendulum
from flask import render_template, g, url_for

from . import requests_bp
from atst.domain.requests import Requests
from atst.models.permissions import Permissions


def map_request(request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()
    app_count = request.body.get("details_of_use", {}).get("num_software_systems", 0)
    annual_usage = request.annual_spend

    if Requests.is_pending_financial_verification(request):
        edit_link = url_for("requests.financial_verification", request_id=request.id)
    elif Requests.is_pending_ccpo_approval(request):
        edit_link = url_for("requests.view_pending_request", request_id=request.id)
    else:
        edit_link = url_for(
            "requests.requests_form_update", screen=1, request_id=request.id
        )

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status_displayname,
        "app_count": app_count,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": request.creator.full_name,
        "annual_usage": annual_usage,
        "edit_link": edit_link,
    }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    if (
        Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST
        in g.current_user.atat_permissions
    ):
        return _ccpo_view()

    else:
        return _non_ccpo_view()


def _ccpo_view():
    requests = Requests.get_many()
    mapped_requests = [map_request(r) for r in requests]

    return render_template(
        "requests.html",
        requests=mapped_requests,
        pending_financial_verification=False,
        pending_ccpo_approval=False,
        extended_view=True,
        kpi_inprogress=Requests.in_progress_count(),
        kpi_pending=Requests.pending_ccpo_count(),
        kpi_completed=Requests.completed_count(),
    )


def _non_ccpo_view():
    requests = Requests.get_many(creator=g.current_user)
    mapped_requests = [map_request(r) for r in requests]

    pending_fv = any(Requests.is_pending_financial_verification(r) for r in requests)
    pending_ccpo = any(Requests.is_pending_ccpo_approval(r) for r in requests)

    return render_template(
        "requests.html",
        requests=mapped_requests,
        pending_financial_verification=pending_fv,
        pending_ccpo_approval=pending_ccpo,
        extended_view=False,
    )
