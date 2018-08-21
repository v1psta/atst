from flask import Blueprint, render_template, request as http_request, g

from atst.domain.workspaces import Workspaces

bp = Blueprint("workspaces", __name__)

@bp.context_processor
def workspace():
    workspace = None
    if "workspace_id" in http_request.view_args:
        workspace = Workspaces.get(http_request.view_args["workspace_id"])
    return { "workspace": workspace }


@bp.route("/workspaces")
def workspaces():
    workspaces = Workspaces.get_many(g.current_user)
    return render_template("workspaces.html", page=5, workspaces=workspaces)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspace_projects.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    members = Members.get_many(workspace_id)
    return render_template("workspace_members.html", members=members)


@bp.route("/workspaces/<workspace_id>/reports")
def workspace_reports(workspace_id):
    return render_template("workspace_reports.html")
