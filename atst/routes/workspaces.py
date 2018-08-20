from flask import Blueprint, render_template, g, Response

from atst.domain.workspaces import Projects, Members, Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.exceptions import NotFoundError


bp = Blueprint("workspaces", __name__)

mock_workspaces = [
    {
        "name": "Unclassified IaaS and PaaS for Defense Digital Service (DDS)",
        "id": "5966187a-eff9-44c3-aa15-4de7a65ac7ff",
        "task_order": {"number": 123456},
        "user_count": 23,
    }
]


@bp.route("/workspaces")
def workspaces():
    workspaces_ = Workspaces.get_many(g.current_user)
    return render_template("workspaces.html", page=5, workspaces=workspaces_)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(workspace_id)

    workspace_user = WorkspaceUsers.get(workspace.id, g.current_user.id)

    # TODO: Not a sufficient check. workspace_user has a value
    # as long as the user exists in the db. Maybe an Authz service?
    if not workspace_user:
        raise NotFoundError("workspace")

    return render_template("workspace_projects.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    members_repo = Members()
    members = members_repo.get_many(workspace_id)
    return render_template(
        "workspace_members.html", workspace_id=workspace_id, members=members
    )


@bp.route("/workspaces/<workspace_id>/projects/<project_id>/edit")
def workspace_project_edit(workspace_id, project_id):
    response_content = "Editing project {} in workspace {}.".format(project_id, workspace_id)
    return Response(response_content)
