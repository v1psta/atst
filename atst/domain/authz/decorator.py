from functools import wraps

from flask import g, current_app as app, request

from . import user_can_access
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.domain.applications import Applications
from atst.domain.invitations import Invitations
from atst.domain.exceptions import UnauthorizedError


def check_access(permission, message, override, *args, **kwargs):
    access_args = {"message": message}

    if "application_id" in kwargs:
        application = Applications.get(kwargs["application_id"])
        access_args["portfolio"] = application.portfolio

    elif "task_order_id" in kwargs:
        task_order = TaskOrders.get(kwargs["task_order_id"])
        access_args["portfolio"] = task_order.portfolio

    elif "token" in kwargs:
        invite = Invitations._get(kwargs["token"])
        access_args["portfolio"] = invite.portfolio_role.portfolio

    elif "portfolio_id" in kwargs:
        access_args["portfolio"] = Portfolios.get(
            g.current_user, kwargs["portfolio_id"]
        )

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
                    "[access] User {} accessed {} {}".format(
                        g.current_user.id, request.method, request.path
                    )
                )

                return f(*args, **kwargs)
            except UnauthorizedError as err:
                app.logger.warning(
                    "[access] User {} denied access {} {}".format(
                        g.current_user.id, request.method, request.path
                    )
                )

                raise (err)

        return decorated_function

    return decorator
