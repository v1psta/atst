from functools import wraps

from flask import g, current_app as app, request

from . import user_can_access
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.domain.applications import Applications
from atst.domain.environments import Environments
from atst.domain.invitations import PortfolioInvitations
from atst.domain.exceptions import UnauthorizedError


def check_access(permission, message, override, *args, **kwargs):
    access_args = {
        "message": message,
        "portfolio": g.portfolio,
        "application": g.application,
    }

    # TODO: We should change the `token` arg in routes to be either
    # `portfolio_token` or `application_token` and have
    # atst.utils.context_processors.assign_resources take care of
    # this.
    if "token" in kwargs:
        invite = PortfolioInvitations._get(kwargs["token"])
        access_args["portfolio"] = invite.role.portfolio

    if override is not None and override(g.current_user, **access_args, **kwargs):
        return True

    user_can_access(g.current_user, permission, **access_args)

    return True


def user_can_access_decorator(permission, message=None, override=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                check_access(permission, message, override, *args, **kwargs)
                app.logger.info(
                    "User {} accessed {} {}".format(
                        g.current_user.id, request.method, request.path
                    ),
                    extra={"tags": ["access", "success"]},
                )

                return f(*args, **kwargs)
            except UnauthorizedError as err:
                app.logger.warning(
                    "User {} denied access {} {}".format(
                        g.current_user.id, request.method, request.path
                    ),
                    extra={"tags": ["access", "failure"]},
                )

                raise (err)

        return decorated_function

    return decorator
