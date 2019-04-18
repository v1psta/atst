from flask import render_template

from . import applications_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


@applications_bp.route("/portfolios/<portfolio_id>/applications")
@user_can(Permissions.VIEW_APPLICATION, message="view portfolio applications")
def portfolio_applications(portfolio_id):
    return render_template("portfolios/applications/index.html")
