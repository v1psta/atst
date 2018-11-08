import pendulum
from flask import render_template, g, url_for

from . import requests_bp
from atst.domain.requests import Requests
from atst.models.permissions import Permissions
from atst.forms.data import SERVICE_BRANCHES


class RequestsIndex(object):
    def __init__(self, user):
        self.user = user

    def execute(self):
        if (
            Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST
            in self.user.atat_permissions
        ):
            context = self._ccpo_view(self.user)

        else:
            context = self._non_ccpo_view(self.user)

        return {
            **context,
            "possible_statuses": Requests.possible_statuses(),
            "possible_dod_components": [b[0] for b in SERVICE_BRANCHES[1:]],
        }

    def _ccpo_view(self, user):
        requests = Requests.get_many()
        mapped_requests = [self._map_request(r, "ccpo") for r in requests]
        num_action_required = len(
            [r for r in mapped_requests if r.get("action_required")]
        )

        return {
            "requests": mapped_requests,
            "pending_financial_verification": False,
            "pending_ccpo_acceptance": False,
            "extended_view": True,
            "kpi_inprogress": Requests.in_progress_count(),
            "kpi_pending": Requests.pending_ccpo_count(),
            "kpi_completed": Requests.completed_count(),
            "num_action_required": num_action_required,
        }

    def _non_ccpo_view(self, user):
        requests = Requests.get_many(creator=user)
        mapped_requests = [self._map_request(r, "mission_owner") for r in requests]
        num_action_required = len(
            [r for r in mapped_requests if r.get("action_required")]
        )
        pending_fv = any(r.is_pending_financial_verification for r in requests)
        pending_ccpo = any(r.is_pending_ccpo_acceptance for r in requests)

        return {
            "requests": mapped_requests,
            "pending_financial_verification": pending_fv,
            "pending_ccpo_acceptance": pending_ccpo,
            "num_action_required": num_action_required,
            "extended_view": False,
        }

    def _workspace_link_for_request(self, request):
        if request.is_approved:
            return url_for(
                "workspaces.workspace_projects", workspace_id=request.workspace.id
            )
        else:
            return None

    def _map_request(self, request, viewing_role):
        time_created = pendulum.instance(request.time_created)
        is_new = time_created.add(days=1) > pendulum.now()
        app_count = request.body.get("details_of_use", {}).get(
            "num_software_systems", 0
        )
        annual_usage = request.annual_spend

        return {
            "workspace_id": request.workspace.id if request.workspace else None,
            "name": request.displayname,
            "is_new": is_new,
            "is_approved": request.is_approved,
            "status": request.status_displayname,
            "app_count": app_count,
            "last_submission_timestamp": request.last_submission_timestamp,
            "last_edited_timestamp": request.latest_revision.time_updated,
            "full_name": request.creator.full_name,
            "annual_usage": annual_usage,
            "edit_link": url_for("requests.edit", request_id=request.id),
            "action_required": request.action_required_by == viewing_role,
            "dod_component": request.latest_revision.dod_component,
            "workspace_link": self._workspace_link_for_request(request),
        }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    context = RequestsIndex(g.current_user).execute()
    return render_template("requests/index.html", **context)
