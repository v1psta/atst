from flask import (
    Blueprint,
    render_template,
    request as http_request,
    g,
    redirect,
    url_for,
)

from atst.domain.exceptions import UnauthorizedError
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from atst.forms.new_project import NewProjectForm
from atst.forms.new_member import NewMemberForm

bp = Blueprint("workspaces", __name__)


@bp.context_processor
def workspace():
    workspace = None
    if "workspace_id" in http_request.view_args:
        try:
            workspace = Workspaces.get(
                g.current_user, http_request.view_args["workspace_id"]
            )
        except UnauthorizedError:
            pass
    return {"workspace": workspace}


@bp.route("/workspaces")
def workspaces():
    workspaces = Workspaces.get_many(g.current_user)
    return render_template("workspaces.html", page=5, workspaces=workspaces)


@bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspace_projects.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>")
def show_workspace(workspace_id):
    return redirect(url_for("workspaces.workspace_projects", workspace_id=workspace_id))


@bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspace_members.html", workspace=workspace)


@bp.route("/workspaces/<workspace_id>/reports")
def workspace_reports(workspace_id):
    return render_template("workspace_reports.html", workspace_id=workspace_id)


@bp.route("/workspaces/<workspace_id>/projects/new")
def new_project(workspace_id):
    workspace = Workspaces.get_for_update(g.current_user, workspace_id)
    form = NewProjectForm()
    return render_template("workspace_project_new.html", workspace=workspace, form=form)


@bp.route("/workspaces/<workspace_id>/projects/new", methods=["POST"])
def update_project(workspace_id):
    workspace = Workspaces.get_for_update(g.current_user, workspace_id)
    form = NewProjectForm(http_request.form)

    if form.validate():
        project_data = form.data
        Projects.create(
            workspace,
            project_data["name"],
            project_data["description"],
            project_data["environment_names"],
        )
        return redirect(
            url_for("workspaces.workspace_projects", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspace_project_new.html", workspace=workspace, form=form
        )


@bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template("member_new.html", workspace=workspace, form=form)
