from functools import wraps

from flask import g

from . import user_can_access
from atst.domain.portfolios import Portfolios


def user_can_access_decorator(permission, message=None, exceptions=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_args = {"message": message}

            if "portfolio_id" in kwargs:
                access_args["portfolio"] = Portfolios.get(
                    g.current_user, kwargs["portfolio_id"]
                )

            if exceptions:
                evaluated = [
                    exc(g.current_user, permission, **access_args) for exc in exceptions
                ]
                if True in evaluated:
                    return True

            user_can_access(g.current_user, permission, **access_args)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
