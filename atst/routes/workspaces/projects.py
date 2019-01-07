from flask import (
    current_app as app,
    g,
    redirect,
    render_template,
    request as http_request,
    url_for,
)

from . import workspaces_bp
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import UnauthorizedError
from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from atst.forms.project import NewProjectForm, ProjectForm


@workspaces_bp.route("/workspaces/<workspace_id>/projects")
def workspace_projects(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspaces/projects/index.html", workspace=workspace)


@workspaces_bp.route("/workspaces/<workspace_id>/projects/new")
def new_project(workspace_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    form = NewProjectForm()
    return render_template(
        "workspaces/projects/new.html", workspace=workspace, form=form
    )


@workspaces_bp.route("/workspaces/<workspace_id>/projects/new", methods=["POST"])
def create_project(workspace_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    form = NewProjectForm(http_request.form)

    if form.validate():
        project_data = form.data
        Projects.create(
            g.current_user,
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
            "workspaces/projects/new.html", workspace=workspace, form=form
        )


@workspaces_bp.route("/workspaces/<workspace_id>/projects/<project_id>/edit")
def edit_project(workspace_id, project_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    project = Projects.get(g.current_user, workspace, project_id)
    form = ProjectForm(name=project.name, description=project.description)

    return render_template(
        "workspaces/projects/edit.html", workspace=workspace, project=project, form=form
    )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/projects/<project_id>/edit", methods=["POST"]
)
def update_project(workspace_id, project_id):
    workspace = Workspaces.get_for_update_projects(g.current_user, workspace_id)
    project = Projects.get(g.current_user, workspace, project_id)
    form = ProjectForm(http_request.form)
    if form.validate():
        project_data = form.data
        Projects.update(g.current_user, workspace, project, project_data)

        return redirect(
            url_for("workspaces.workspace_projects", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/projects/edit.html",
            workspace=workspace,
            project=project,
            form=form,
        )


@workspaces_bp.route("/workspaces/<workspace_id>/environments/<environment_id>/access")
def access_environment(workspace_id, environment_id):
    env_role = EnvironmentRoles.get(g.current_user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(
            g.current_user, "access environment {}".format(environment_id)
        )
    else:
        token = app.csp.cloud.get_access_token(env_role)
        return redirect(url_for("atst.csp_environment_access", token=token))
