from flask import Blueprint, render_template, g, redirect, url_for, request as http_request
from atst.forms.edit_user import EditUserForm
from atst.domain.users import Users


bp = Blueprint("users", __name__)


@bp.route("/user")
def user():
    user = g.current_user
    form = EditUserForm(data=user.to_dictionary())
    return render_template("user/edit.html", form=form, user=user)


@bp.route("/user", methods=["POST"])
def update_user():
    user = g.current_user
    form = EditUserForm(http_request.form)
    if form.validate():
        Users.update(user, form.data)
        return redirect(url_for("atst.home"))
    else:
        return render_template("user/edit.html", form=form, user=user)

