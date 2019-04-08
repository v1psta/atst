from flask import (
    current_app as app,
    g,
    redirect,
    render_template,
    request as http_request,
    url_for,
)

from . import portfolios_bp
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.exceptions import UnauthorizedError
from atst.domain.applications import Applications
from atst.domain.portfolios import Portfolios
from atst.forms.application import NewApplicationForm, ApplicationForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash
from atst.domain.permission_sets import PermissionSets
from atst.utils.localization import translate


@portfolios_bp.route("/portfolios/<portfolio_id>/applications")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def portfolio_applications(portfolio_id):
    return render_template("portfolios/applications/index.html")


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new")
@user_can(Permissions.CREATE_APPLICATION, message="view create new application form")
def new_application(portfolio_id):
    form = NewApplicationForm()
    return render_template("portfolios/applications/new.html", form=form)


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new", methods=["POST"])
@user_can(Permissions.CREATE_APPLICATION, message="create new application")
def create_application(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = NewApplicationForm(http_request.form)

    if form.validate():
        application_data = form.data
        Applications.create(
            portfolio,
            application_data["name"],
            application_data["description"],
            application_data["environment_names"],
        )
        return redirect(
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
        )
    else:
        return render_template("portfolios/applications/new.html", form=form)


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


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/<application_id>/edit")
@user_can(Permissions.EDIT_APPLICATION, message="view application edit form")
def edit_application(portfolio_id, application_id):
    application = Applications.get(application_id, portfolio_id=portfolio_id)
    form = ApplicationForm(name=application.name, description=application.description)

    return render_template(
        "portfolios/applications/edit.html",
        application=application,
        form=form,
        environments_obj=get_environments_obj_for_app(application=application),
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/applications/<application_id>/edit", methods=["POST"]
)
@user_can(Permissions.EDIT_APPLICATION, message="update application")
def update_application(portfolio_id, application_id):
    application = Applications.get(application_id, portfolio_id=portfolio_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(application, application_data)

        return redirect(
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
        )
    else:
        return render_template(
            "portfolios/applications/edit.html",
            application=application,
            form=form,
            environments_obj=get_environments_obj_for_app(application=application),
        )


def wrap_environment_role_lookup(
    user, portfolio_id=None, environment_id=None, **kwargs
):
    env_role = EnvironmentRoles.get_for_portfolio(
        user.id, environment_id, portfolio_id=portfolio_id
    )
    if not env_role:
        raise UnauthorizedError(user, "access environment {}".format(environment_id))

    return True


@portfolios_bp.route("/portfolios/<portfolio_id>/environments/<environment_id>/access")
@user_can(None, override=wrap_environment_role_lookup, message="access environment")
def access_environment(portfolio_id, environment_id):
    env_role = EnvironmentRoles.get_for_portfolio(
        g.current_user.id, environment_id, portfolio_id=portfolio_id
    )
    token = app.csp.cloud.get_access_token(env_role)

    return redirect(url_for("atst.csp_environment_access", token=token))


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/applications/<application_id>/delete", methods=["POST"]
)
@user_can(Permissions.DELETE_APPLICATION, message="delete application")
def delete_application(portfolio_id, application_id):
    application = Applications.get(application_id, portfolio_id=portfolio_id)
    Applications.delete(application)

    flash("application_deleted", application_name=application.name)

    return redirect(
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
    )


def permission_str(member, edit_perm_set):
    if member.has_permission_set(edit_perm_set):
        return translate("portfolios.members.permissions.edit_access")
    else:
        return translate("portfolios.members.permissions.view_only")


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/<application_id>/team")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def application_team(portfolio_id, application_id):
    application = Applications.get(application_id)
    portfolio = Portfolios.get(g.current_user, portfolio_id)

    environment_users = {}
    for member in application.members:
        user_id = member.user.id
        environment_users[user_id] = {
            "permissions": {
                "delete_access": permission_str(
                    member, PermissionSets.DELETE_APPLICATION_ENVIRONMENTS
                ),
                "environment_management": permission_str(
                    member, PermissionSets.EDIT_APPLICATION_ENVIRONMENTS
                ),
                "team_management": permission_str(
                    member, PermissionSets.EDIT_APPLICATION_TEAM
                ),
            },
            "environments": Environments.for_user(
                user=member.user, application=application
            ),
        }

    return render_template(
        "portfolios/applications/team.html",
        application=application,
        portfolio=portfolio,
        environment_users=environment_users,
    )
