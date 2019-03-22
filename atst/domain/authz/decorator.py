from functools import wraps

from flask import g, current_app as app, request

from . import user_can_access
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.domain.exceptions import UnauthorizedError


def check_access(permission, message, exception, *args, **kwargs):
    access_args = {"message": message}

    if "portfolio_id" in kwargs:
        access_args["portfolio"] = Portfolios.get(
            g.current_user, kwargs["portfolio_id"]
        )
    elif "task_order_id" in kwargs:
        task_order = TaskOrders.get(kwargs["task_order_id"])
        access_args["portfolio"] = task_order.portfolio

    if exception is not None and exception(g.current_user, **access_args, **kwargs):
        return True

    user_can_access(g.current_user, permission, **access_args)

    return True


def user_can_access_decorator(permission, message=None, exception=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                check_access(permission, message, exception, *args, **kwargs)
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
