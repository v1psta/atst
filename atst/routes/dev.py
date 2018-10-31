from flask import (
    Blueprint,
    request,
    session,
    redirect,
    render_template,
    url_for,
    current_app as app,
)

from . import redirect_after_login_url
from atst.domain.users import Users
from atst.queue import queue

bp = Blueprint("dev", __name__)

_DEV_USERS = {
    "sam": {
        "dod_id": "6346349876",
        "first_name": "Sam",
        "last_name": "Stevenson",
        "atat_role_name": "ccpo",
        "email": "sam@example.com",
    },
    "amanda": {
        "dod_id": "2345678901",
        "first_name": "Amanda",
        "last_name": "Adamson",
        "atat_role_name": "default",
        "email": "amanda@example.com",
    },
    "brandon": {
        "dod_id": "3456789012",
        "first_name": "Brandon",
        "last_name": "Buchannan",
        "atat_role_name": "default",
        "email": "brandon@example.com",
    },
    "christina": {
        "dod_id": "4567890123",
        "first_name": "Christina",
        "last_name": "Collins",
        "atat_role_name": "default",
        "email": "christina@example.com",
    },
    "dominick": {
        "dod_id": "5678901234",
        "first_name": "Dominick",
        "last_name": "Domingo",
        "atat_role_name": "default",
        "email": "dominick@example.com",
    },
    "erica": {
        "dod_id": "6789012345",
        "first_name": "Erica",
        "last_name": "Eichner",
        "atat_role_name": "default",
        "email": "erica@example.com",
    },
}


@bp.route("/login-dev")
def login_dev():
    role = request.args.get("username", "amanda")
    user_data = _DEV_USERS[role]
    user = Users.get_or_create_by_dod_id(
        user_data["dod_id"],
        atat_role_name=user_data["atat_role_name"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
    )
    session["user_id"] = user.id

    return redirect(redirect_after_login_url())


@bp.route("/test-email")
def test_email():
    queue.send_mail(
        [request.args.get("to")], request.args.get("subject"), request.args.get("body")
    )

    return redirect(url_for("dev.messages"))


@bp.route("/messages")
def messages():
    return render_template("dev/emails.html", messages=app.mailer.messages)
