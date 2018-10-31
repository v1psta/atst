from flask import Blueprint, render_template, g, request as http_request, redirect
from atst.forms.edit_user import EditUserForm
from atst.domain.users import Users


bp = Blueprint("users", __name__)


@bp.route("/user")
def user():
    user = g.current_user
    form = EditUserForm(data=user.to_dictionary())
    return render_template(
        "user/edit.html", next=http_request.args.get("next"), form=form, user=user
    )


@bp.route("/user", methods=["POST"])
def update_user():
    user = g.current_user
    form = EditUserForm(http_request.form)
    next_url = http_request.args.get("next")
    rerender_args = {"form": form, "user": user, "next": next_url}
    if form.validate():
        Users.update(user, form.data)
        rerender_args["updated"] = True
        if next_url:
            return redirect(next_url)

    return render_template("user/edit.html", **rerender_args)
