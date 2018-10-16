from flask import Blueprint, render_template, g, request as http_request
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
    rerender_args = {"form": form, "user": user}
    if form.validate():
        Users.update(user, form.data)
        rerender_args["updated"] = True

    return render_template("user/edit.html", **rerender_args)
