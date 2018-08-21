from flask import Blueprint, render_template, request as http_request

from atst.domain.workspaces import Members, Projects, Workspaces


bp = Blueprint("workspaces", __name__)

@bp.context_processor
def workspace():
    workspace = None
    if "workspace_id" in http_request.view_args:
        workspace = Workspaces.get(http_request.view_args["workspace_id"])
    return { "workspace": workspace }


@bp.route("/workspaces")
def workspaces():
    return render_template("workspaces.html", page=5, workspaces=Workspaces.get_many())


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    projects = Projects.get_many(workspace_id)
    return render_template("workspace_projects.html", projects=projects)


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    members = Members.get_many(workspace_id)
    return render_template("workspace_members.html", members=members)


@bp.route("/workspaces/<workspace_id>/reports")
def workspace_reports(workspace_id):
    return render_template("workspace_reports.html")
