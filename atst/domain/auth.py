from functools import wraps
from flask import g, request, redirect, url_for, session

from atst.domain.users import Users


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            g.user = Users.get(session.get("user_id"))
            return f(*args, **kwargs)

        else:
            return redirect(url_for("atst.root"))

    return decorated_function
