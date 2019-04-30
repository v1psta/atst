from flask import redirect, render_template, request as http_request, url_for

from . import applications_bp
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.forms.app_settings import EnvironmentRolesForm
from atst.forms.application import ApplicationForm, EditEnvironmentForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.exceptions import NotFoundError

from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def get_environments_obj_for_app(application):
    environments_obj = {}

    for env in application.environments:
        environments_obj[env.name] = {
            "edit_form": EditEnvironmentForm(obj=env),
            "id": env.id,
            "members": [],
        }
        for user in env.users:
            env_role = EnvironmentRoles.get(user.id, env.id)
            environments_obj[env.name]["members"].append(
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


def check_users_are_in_application(user_ids, application):
    existing_ids = [str(role.user_id) for role in application.roles]
    for user_id in user_ids:
        if not user_id in existing_ids:
            raise NotFoundError("application user", user_id)
    return True


@applications_bp.route("/applications/<application_id>/settings")
@user_can(Permissions.VIEW_APPLICATION, message="view application edit form")
def settings(application_id):
    # refactor like portfolio admin render function
    application = Applications.get(application_id)
    form = ApplicationForm(name=application.name, description=application.description)
    app_envs_data = serialize_env_member_form_data(application)

    env_forms = {}
    for env_data in app_envs_data:
        env_forms[env_data["env_id"]] = EnvironmentRolesForm(data=env_data)

    return render_template(
        "portfolios/applications/settings.html",
        application=application,
        form=form,
        environments_obj=get_environments_obj_for_app(application=application),
        env_forms=env_forms,
    )


@applications_bp.route("/environments/<environment_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_ENVIRONMENT, message="edit application environments")
def update_environment(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application

    form = EditEnvironmentForm(formdata=http_request.form)

    if form.validate():
        Environments.update(environment=environment, name=form.name.data)

    flash("application_environments_updated")

    return redirect(
        url_for(
            "applications.settings",
            application_id=application.id,
            fragment="application-environments",
            _anchor="application-environments",
        )
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
            "portfolios/applications/settings.html",
            application=application,
            form=form,
            environments_obj=get_environments_obj_for_app(application=application),
            env_forms=env_forms,
        )


@applications_bp.route("/environments/<environment_id>/roles", methods=["POST"])
@user_can(Permissions.ASSIGN_ENVIRONMENT_MEMBER, message="update environment roles")
def update_env_roles(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application
    env_roles_form = EnvironmentRolesForm(http_request.form)

    if env_roles_form.validate():

        try:
            user_ids = [user["user_id"] for user in env_roles_form.data["team_roles"]]
            check_users_are_in_application(user_ids, application)
        except NotFoundError as err:
            app.logger.warning(
                "User {} requested environment role change for unauthorized user {} in application {}.".format(
                    g.current_user.id, err.resource_id, application.id
                ),
                extra={"tags": ["update", "failure"], "security_warning": True},
            )

            raise (err)
        env_data = env_roles_form.data
        Environments.update_env_roles_by_environment(
            environment_id=environment_id, team_roles=env_data["team_roles"]
        )
        return redirect(url_for("applications.settings", application_id=application.id))
    else:
        # TODO: Create a better pattern to handle when a form doesn't validate
        # if a user is submitting the data via the web page then they
        # should never have any form validation errors
        return render_template(
            "portfolios/applications/settings.html",
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
