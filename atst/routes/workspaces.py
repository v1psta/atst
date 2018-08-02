from flask import Blueprint, render_template

from atst.domain.workspaces import Projects, Members
from atst.database import db

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
    return render_template("workspaces.html", page=5, workspaces=mock_workspaces)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    projects_repo = Projects()
    projects = projects_repo.get_many(workspace_id)
    return render_template(
        "workspace_projects.html", workspace_id=workspace_id, projects=projects
    )


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    members_repo = Members()
    members = members_repo.get_many(workspace_id)
    return render_template(
        "workspace_members.html", workspace_id=workspace_id, members=members
    )
