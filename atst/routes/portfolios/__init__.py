from flask import Blueprint, request as http_request, g, render_template

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

    return {"portfolio": portfolio, "permissions": Permissions, "user_can": user_can}
