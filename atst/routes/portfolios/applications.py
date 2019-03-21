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
from atst.domain.exceptions import UnauthorizedError
from atst.domain.applications import Applications
from atst.domain.portfolios import Portfolios
from atst.forms.application import NewApplicationForm, ApplicationForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


@portfolios_bp.route("/portfolios/<portfolio_id>/applications")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def portfolio_applications(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    return render_template("portfolios/applications/index.html", portfolio=portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new")
@user_can(Permissions.CREATE_APPLICATION, message="view create new application form")
def new_application(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = NewApplicationForm()
    return render_template(
        "portfolios/applications/new.html", portfolio=portfolio, form=form
    )


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
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        return render_template(
            "portfolios/applications/new.html", portfolio=portfolio, form=form
        )


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/<application_id>/edit")
@user_can(Permissions.EDIT_APPLICATION, message="view application edit form")
def edit_application(portfolio_id, application_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    application = Applications.get(application_id)
    form = ApplicationForm(name=application.name, description=application.description)

    return render_template(
        "portfolios/applications/edit.html",
        portfolio=portfolio,
        application=application,
        form=form,
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/applications/<application_id>/edit", methods=["POST"]
)
@user_can(Permissions.EDIT_APPLICATION, message="update application")
def update_application(portfolio_id, application_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    application = Applications.get(application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(application, application_data)

        return redirect(
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        return render_template(
            "portfolios/applications/edit.html",
            portfolio=portfolio,
            application=application,
            form=form,
        )


def wrap_environment_role_lookup(
    user, _perm, portfolio_id=None, environment_id=None, **kwargs
):
    env_role = EnvironmentRoles.get(user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(user, "access environment {}".format(environment_id))

    return True


@portfolios_bp.route("/portfolios/<portfolio_id>/environments/<environment_id>/access")
@user_can(None, exceptions=[wrap_environment_role_lookup], message="access environment")
def access_environment(portfolio_id, environment_id):
    env_role = EnvironmentRoles.get(g.current_user.id, environment_id)
    token = app.csp.cloud.get_access_token(env_role)

    return redirect(url_for("atst.csp_environment_access", token=token))
