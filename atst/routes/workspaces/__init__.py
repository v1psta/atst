from flask import Blueprint, request as http_request, g, render_template

workspaces_bp = Blueprint("workspaces", __name__)

from . import index
from . import projects
from . import members
from . import invitations
from . import new
from atst.domain.exceptions import UnauthorizedError
from atst.domain.workspaces import Workspaces
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions


@workspaces_bp.context_processor
def workspace():
    workspaces = Workspaces.for_user(g.current_user)
    workspace = None
    if "workspace_id" in http_request.view_args:
        try:
            workspace = Workspaces.get(
                g.current_user, http_request.view_args["workspace_id"]
            )
            workspaces = [ws for ws in workspaces if not ws.id == workspace.id]
        except UnauthorizedError:
            pass

    def user_can(permission):
        if workspace:
            return Authorization.has_workspace_permission(
                g.current_user, workspace, permission
            )
        return False

    return {
        "workspace": workspace,
        "workspaces": workspaces,
        "permissions": Permissions,
        "user_can": user_can,
    }
