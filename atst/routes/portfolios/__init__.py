from flask import Blueprint, request as http_request, g, render_template
from operator import attrgetter

portfolios_bp = Blueprint("portfolios", __name__)

from . import index
from . import applications
from . import members
from . import invitations
from . import task_orders
from atst.domain.exceptions import UnauthorizedError
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions


@portfolios_bp.context_processor
def portfolio():
    portfolio = None
    if "portfolio_id" in http_request.view_args:
        try:
            portfolio = Portfolios.get(
                g.current_user, http_request.view_args["portfolio_id"]
            )
        except UnauthorizedError:
            pass

    def user_can(permission):
        if portfolio:
            return Authorization.has_portfolio_permission(
                g.current_user, portfolio, permission
            )
        return False

    active_task_orders = [
        task_order for task_order in portfolio.task_orders if task_order.is_active
    ]
    funding_end_date = (
        sorted(active_task_orders, key=attrgetter("end_date"))[-1].end_date
        if active_task_orders
        else None
    )
    funded = len(active_task_orders) > 1

    return {
        "portfolio": portfolio,
        "permissions": Permissions,
        "user_can": user_can,
        "funding_end_date": funding_end_date,
        "funded": funded,
    }
