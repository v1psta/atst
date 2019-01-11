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


@portfolios_bp.route("/portfolios/<portfolio_id>/applications")
def portfolio_applications(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    return render_template("portfolios/applications/index.html", portfolio=portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new")
def new_application(portfolio_id):
    portfolio = Portfolios.get_for_update_applications(g.current_user, portfolio_id)
    form = NewApplicationForm()
    return render_template(
        "portfolios/applications/new.html", portfolio=portfolio, form=form
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/applications/new", methods=["POST"])
def create_application(portfolio_id):
    portfolio = Portfolios.get_for_update_applications(g.current_user, portfolio_id)
    form = NewApplicationForm(http_request.form)

    if form.validate():
        application_data = form.data
        Applications.create(
            g.current_user,
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
def edit_application(portfolio_id, application_id):
    portfolio = Portfolios.get_for_update_applications(g.current_user, portfolio_id)
    application = Applications.get(g.current_user, portfolio, application_id)
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
def update_application(portfolio_id, application_id):
    portfolio = Portfolios.get_for_update_applications(g.current_user, portfolio_id)
    application = Applications.get(g.current_user, portfolio, application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(g.current_user, portfolio, application, application_data)

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
def access_environment(portfolio_id, environment_id):
    env_role = EnvironmentRoles.get(g.current_user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(
            g.current_user, "access environment {}".format(environment_id)
        )
    else:
        token = app.csp.cloud.get_access_token(env_role)
        return redirect(url_for("atst.csp_environment_access", token=token))
