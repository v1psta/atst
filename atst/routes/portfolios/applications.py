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
@user_can(Permissions.VIEW_APPLICATION)
def portfolio_applications(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    return render_template("portfolios/applications/index.html", portfolio=portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new")
@user_can(Permissions.CREATE_APPLICATION)
def new_application(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = NewApplicationForm()
    return render_template(
        "portfolios/applications/new.html", portfolio=portfolio, form=form
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new", methods=["POST"])
@user_can(Permissions.CREATE_APPLICATION)
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
@user_can(Permissions.EDIT_APPLICATION)
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
@user_can(Permissions.EDIT_APPLICATION)
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


@portfolios_bp.route("/portfolios/<portfolio_id>/environments/<environment_id>/access")
# TODO: we probably need a different permission for this
@user_can(Permissions.VIEW_ENVIRONMENT)
def access_environment(portfolio_id, environment_id):
    env_role = EnvironmentRoles.get(g.current_user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(
            g.current_user, "access environment {}".format(environment_id)
        )
    else:
        token = app.csp.cloud.get_access_token(env_role)
        return redirect(url_for("atst.csp_environment_access", token=token))
