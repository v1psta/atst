from flask import redirect, render_template, request as http_request, url_for

from . import applications_bp
from atst.domain.applications import Applications
from atst.domain.portfolios import Portfolios
from atst.forms.application import NewApplicationForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


@applications_bp.route("/portfolios/<portfolio_id>/applications/new")
@user_can(Permissions.CREATE_APPLICATION, message="view create new application form")
def new(portfolio_id):
    form = NewApplicationForm()
    return render_template("portfolios/applications/new.html", form=form)


@applications_bp.route("/portfolios/<portfolio_id>/applications", methods=["POST"])
@user_can(Permissions.CREATE_APPLICATION, message="create new application")
def create(portfolio_id):
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
            url_for("applications.portfolio_applications", portfolio_id=portfolio_id)
        )
    else:
        return render_template("portfolios/applications/new.html", form=form)
