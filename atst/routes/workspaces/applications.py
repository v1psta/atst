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
from atst.domain.applications import Applications
from atst.domain.workspaces import Workspaces
from atst.forms.application import NewApplicationForm, ApplicationForm


@workspaces_bp.route("/workspaces/<workspace_id>/applications")
def workspace_applications(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspaces/applications/index.html", workspace=workspace)


@workspaces_bp.route("/workspaces/<workspace_id>/applications/new")
def new_application(workspace_id):
    workspace = Workspaces.get_for_update_applications(g.current_user, workspace_id)
    form = NewApplicationForm()
    return render_template(
        "workspaces/applications/new.html", workspace=workspace, form=form
    )


@workspaces_bp.route("/workspaces/<workspace_id>/applications/new", methods=["POST"])
def create_application(workspace_id):
    workspace = Workspaces.get_for_update_applications(g.current_user, workspace_id)
    form = NewApplicationForm(http_request.form)

    if form.validate():
        application_data = form.data
        Applications.create(
            g.current_user,
            workspace,
            application_data["name"],
            application_data["description"],
            application_data["environment_names"],
        )
        return redirect(
            url_for("workspaces.workspace_applications", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/applications/new.html", workspace=workspace, form=form
        )


@workspaces_bp.route("/workspaces/<workspace_id>/applications/<application_id>/edit")
def edit_application(workspace_id, application_id):
    workspace = Workspaces.get_for_update_applications(g.current_user, workspace_id)
    application = Applications.get(g.current_user, workspace, application_id)
    form = ApplicationForm(name=application.name, description=application.description)

    return render_template(
        "workspaces/applications/edit.html",
        workspace=workspace,
        application=application,
        form=form,
    )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/applications/<application_id>/edit", methods=["POST"]
)
def update_application(workspace_id, application_id):
    workspace = Workspaces.get_for_update_applications(g.current_user, workspace_id)
    application = Applications.get(g.current_user, workspace, application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(g.current_user, workspace, application, application_data)

        return redirect(
            url_for("workspaces.workspace_applications", workspace_id=workspace.id)
        )
    else:
        return render_template(
            "workspaces/applications/edit.html",
            workspace=workspace,
            application=application,
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
