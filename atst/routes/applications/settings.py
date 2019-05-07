from flask import redirect, render_template, request as http_request, url_for

from . import applications_bp
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.forms.app_settings import AppEnvRolesForm
from atst.forms.application import ApplicationForm, EditEnvironmentForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.environment_role import CSPRole
from atst.domain.exceptions import NotFoundError
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def get_environments_obj_for_app(application):
    environments_obj = []
    for env in application.environments:
        env_data = {
            "id": env.id,
            "name": env.name,
            "edit_form": EditEnvironmentForm(obj=env),
            "member_count": len(env.users),
            "members": [user.full_name for user in env.users],
        }
        environments_obj.append(env_data)

    return environments_obj


def sort_env_users_by_role(env):
    users_list = []
    no_access_users = env.application.users - env.users
    no_access_list = [
        {"user_id": str(user.id), "user_name": user.full_name, "role": "no_access"}
        for user in no_access_users
    ]
    users_list.append({"role": "no_access", "members": no_access_list})

    for role in CSPRole:
        users_list.append(
            {
                "role": role.value,
                "members": Environments.get_members_by_role(env, role.value),
            }
        )

    return users_list


def data_for_app_env_roles_form(application):
    data = {"envs": []}
    for environment in application.environments:
        data["envs"].append(
            {
                "env_id": environment.id,
                "team_roles": sort_env_users_by_role(environment),
            }
        )

    return data


def check_users_are_in_application(user_ids, application):
    existing_ids = [str(role.user_id) for role in application.roles]
    for user_id in user_ids:
        if not user_id in existing_ids:
            raise NotFoundError("application user", user_id)
    return True


@applications_bp.route("/applications/<application_id>/settings")
@user_can(Permissions.VIEW_APPLICATION, message="view application edit form")
def settings(application_id):
    application = Applications.get(application_id)
    form = ApplicationForm(name=application.name, description=application.description)
    environments_obj = get_environments_obj_for_app(application=application)
    members_form = AppEnvRolesForm(data=data_for_app_env_roles_form(application))

    return render_template(
        "portfolios/applications/settings.html",
        application=application,
        form=form,
        environments_obj=environments_obj,
        members_form=members_form,
        active_toggler=http_request.args.get("active_toggler"),
        active_toggler_section=http_request.args.get("active_toggler_section"),
    )


@applications_bp.route("/environments/<environment_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_ENVIRONMENT, message="edit application environments")
def update_environment(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application

    env_form = EditEnvironmentForm(obj=environment, formdata=http_request.form)

    if env_form.validate():
        Environments.update(environment=environment, name=env_form.name.data)

        flash("application_environments_updated")

        return redirect(
            url_for(
                "applications.settings",
                application_id=application.id,
                fragment="application-environments",
                _anchor="application-environments",
                active_toggler=environment.id,
                active_toggler_section="edit",
            )
        )
    else:
        return (
            render_template(
                "portfolios/applications/settings.html",
                application=application,
                form=ApplicationForm(
                    name=application.name, description=application.description
                ),
                environments_obj=get_environments_obj_for_app(application=application),
                members_form=AppEnvRolesForm(
                    data=data_for_app_env_roles_form(application)
                ),
                active_toggler=environment.id,
                active_toggler_section="edit",
            ),
            400,
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
        return render_template(
            "portfolios/applications/settings.html",
            application=application,
            form=form,
            environments_obj=get_environments_obj_for_app(application=application),
        )


@applications_bp.route("/environments/<environment_id>/roles", methods=["POST"])
@user_can(Permissions.ASSIGN_ENVIRONMENT_MEMBER, message="update environment roles")
def update_env_roles(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application
    form = AppEnvRolesForm(formdata=http_request.form)

    if form.validate():
        env_data = []
        try:
            for env in form.envs.data:
                if env["env_id"] == str(environment.id):
                    for role in env["team_roles"]:
                        user_ids = [user["user_id"] for user in role["members"]]
                        check_users_are_in_application(user_ids, application)
                        env_data = env_data + role["members"]
        except NotFoundError as err:
            app.logger.warning(
                "User {} requested environment role change for unauthorized user {} in application {}.".format(
                    g.current_user.id, err.resource_id, application.id
                ),
                extra={"tags": ["update", "failure"], "security_warning": True},
            )

            raise (err)

        Environments.update_env_roles_by_environment(
            environment_id=environment_id, team_roles=env_data
        )

        flash("application_environment_members_updated")

        return redirect(
            url_for(
                "applications.settings",
                application_id=application.id,
                fragment="application-environments",
                _anchor="application-environments",
                active_toggler=environment.id,
                active_toggler_section="members",
            )
        )
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
            active_toggler=environment.id,
            active_toggler_section="edit",
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


@applications_bp.route("/environments/<environment_id>/delete", methods=["POST"])
@user_can(Permissions.DELETE_ENVIRONMENT, message="delete environment")
def delete_environment(environment_id):
    environment = Environments.get(environment_id)
    Environments.delete(environment=environment, commit=True)

    flash("environment_deleted", environment_name=environment.name)

    return redirect(
        url_for(
            "applications.settings",
            application_id=environment.application_id,
            _anchor="application-environments",
            fragment="application-environments",
        )
    )
