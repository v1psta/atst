from flask import Blueprint, request, session, redirect

from . import redirect_url
from atst.domain.users import Users

bp = Blueprint("dev", __name__)

_DEV_USERS = {
    "sam": {
        "dod_id": "1234567890",
        "first_name": "Sam",
        "last_name": "Seeceepio",
        "atat_role_name": "ccpo",
        "email": "sam@test.com",
    },
    "amanda": {
        "dod_id": "2345678901",
        "first_name": "Amanda",
        "last_name": "Adamson",
        "atat_role_name": "default",
        "email": "amanda@test.com",
    },
    "brandon": {
        "dod_id": "3456789012",
        "first_name": "Brandon",
        "last_name": "Buchannan",
        "atat_role_name": "default",
        "email": "brandon@test.com",
    },
    "christina": {
        "dod_id": "4567890123",
        "first_name": "Christina",
        "last_name": "Collins",
        "atat_role_name": "default",
        "email": "christina@test.com",
    },
    "dominick": {
        "dod_id": "5678901234",
        "first_name": "Dominick",
        "last_name": "Domingo",
        "atat_role_name": "default",
        "email": "dominick@test.com",
    },
    "erica": {
        "dod_id": "6789012345",
        "first_name": "Erica",
        "last_name": "Eichner",
        "atat_role_name": "default",
        "email": "erica@test.com",
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

    return redirect(redirect_url())
