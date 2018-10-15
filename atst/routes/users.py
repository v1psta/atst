from flask import Blueprint, render_template, g, redirect, session, url_for, request
from atst.forms.edit_user import EditUserForm


bp = Blueprint("users", __name__)


@bp.route("/user")
def user():
    user = g.current_user
    form = EditUserForm(data=user.to_dictionary())
    return render_template("user/edit.html", form=form, user=user)


@bp.route("/user", methods=["POST"])
def update_user():
    return redirect(url_for(".home"))
