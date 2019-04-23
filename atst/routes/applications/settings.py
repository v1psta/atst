from flask import redirect, render_template, request as http_request, url_for

from . import applications_bp
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.forms.application import ApplicationForm
from atst.forms.app_settings import EnvironmentRolesForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def get_environments_obj_for_app(application):
    environments_obj = {}

    for env in application.environments:
        environments_obj[env.name] = []
        for user in env.users:
            env_role = EnvironmentRoles.get(user.id, env.id)
            environments_obj[env.name].append(
                {"name": user.full_name, "role": env_role.displayname}
            )

    return environments_obj


def serialize_env_member_form_data(application):
    environments_list = []
    for env in application.environments:
        env_info = {"env_id": env.id, "team_roles": []}
        for user in env.users:
            env_role = EnvironmentRoles.get(user.id, env.id)
            env_info["team_roles"].append(
                {
                    "name": user.full_name,
                    "user_id": user.id,
                    "role": env_role.displayname,
                }
            )
        environments_list.append(env_info)
    return environments_list


@applications_bp.route("/applications/<application_id>/settings")
@user_can(Permissions.VIEW_APPLICATION, message="view application edit form")
def settings(application_id):
    application = Applications.get(application_id)
    form = ApplicationForm(name=application.name, description=application.description)
    env_data = serialize_env_member_form_data(application)
    env_forms = {}
    for data in env_data:
        env_forms[data["env_id"]] = EnvironmentRolesForm(data=data)

    return render_template(
        "portfolios/applications/edit.html",
        application=application,
        form=form,
        environments_obj=get_environments_obj_for_app(application=application),
        env_forms=env_forms,
    )


@applications_bp.route("/applications/<application_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_APPLICATION, message="update application")
def update(application_id):
    application = Applications.get(application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(application, application_data)

        return redirect(
            url_for(
                "applications.portfolio_applications",
                portfolio_id=application.portfolio_id,
            )
        )
    else:
        env_data = serialize_env_member_form_data(application)
        env_forms = {}
        for data in env_data:
            env_forms[data["env_id"]] = EnvironmentRolesForm(data=data)

        return render_template(
            "portfolios/applications/edit.html",
            application=application,
            form=form,
            environments_obj=get_environments_obj_for_app(application=application),
            env_forms=env_forms,
        )


@applications_bp.route(
    "/applications/<application_id>/update_env_roles", methods=["POST"]
)
@user_can(Permissions.ASSIGN_ENVIRONMENT_MEMBER, message="update application")
def update_env_roles(application_id):
    application = Applications.get(application_id)
    env_roles_form = EnvironmentRolesForm(http_request.form)

    if env_roles_form.validate():
        env_data = env_roles_form.data
        Environments.update_env_roles_by_environment(
            environment_id=env_data["env_id"], team_roles=env_data["team_roles"]
        )
        return redirect(url_for("applications.settings", application_id=application.id))
    else:
        return render_template(
            "portfolios/applications/edit.html",
            application=application,
            form=ApplicationForm(
                name=application.name, description=application.description
            ),
            environments_obj=get_environments_obj_for_app(application=application),
            env_forms=env_roles_form,
        )


@applications_bp.route("/applications/<application_id>/delete", methods=["POST"])
@user_can(Permissions.DELETE_APPLICATION, message="delete application")
def delete(application_id):
    application = Applications.get(application_id)
    Applications.delete(application)

    flash("application_deleted", application_name=application.name)

    return redirect(
        url_for(
            "applications.portfolio_applications", portfolio_id=application.portfolio_id
        )
    )
