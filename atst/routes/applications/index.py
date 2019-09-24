from flask import render_template

from . import applications_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


def has_portfolio_applications(_user, portfolio=None, **_kwargs):
    """
    If the portfolio exists and the user has access to applications
    within the scoped portfolio, the user has access to the
    portfolio landing page.
    """
    if portfolio and portfolio.applications:
        return True


@applications_bp.route("/portfolios/<portfolio_id>")
@applications_bp.route("/portfolios/<portfolio_id>/applications")
@user_can(
    Permissions.VIEW_APPLICATION,
    override=has_portfolio_applications,
    message="view portfolio applications",
)
def portfolio_applications(portfolio_id):
    return render_template("applications/index.html")
