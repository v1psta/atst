from functools import wraps
from flask import g, redirect, url_for, session

from atst.domain.users import Users


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user:
            g.current_user = user
            return f(*args, **kwargs)

        else:
            return redirect(url_for("atst.root"))

    return decorated_function

def get_current_user():
    user_id = session.get("user_id")
    if user_id:
        return Users.get(user_id)
    else:
        return False
