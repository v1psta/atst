from flask import Blueprint, render_template, redirect, url_for, request
from atst.domain.users import Users
from atst.domain.audit_log import AuditLog
from atst.domain.common import Paginator
from atst.domain.exceptions import NotFoundError
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.forms.ccpo_user import CCPOUserForm
from atst.models.permissions import Permissions
from atst.utils.context_processors import atat as atat_context_processor
from atst.utils.flash import formatted_flash as flash


bp = Blueprint("ccpo", __name__)
bp.context_processor(atat_context_processor)


@bp.route("/activity-history")
@user_can(Permissions.VIEW_AUDIT_LOG, message="view activity log")
def activity_history():
    pagination_opts = Paginator.get_pagination_opts(request)
    audit_events = AuditLog.get_all_events(pagination_opts)
    return render_template("audit_log/audit_log.html", audit_events=audit_events)


@bp.route("/ccpo-users")
@user_can(Permissions.VIEW_CCPO_USER, message="view ccpo users")
def users():
    users = Users.get_ccpo_users()
    return render_template("ccpo/users.html", users=users)


@bp.route("/ccpo-users/new")
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def add_new_user():
    form = CCPOUserForm()
    return render_template("ccpo/add_user.html", form=form)


@bp.route("/ccpo-users/new", methods=["POST"])
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def submit_new_user():
    try:
        new_user = Users.get_by_dod_id(request.form["dod_id"])
        form = CCPOUserForm(obj=new_user)
    except NotFoundError:
        new_user = None
        form = CCPOUserForm()

    return render_template("ccpo/confirm_user.html", new_user=new_user, form=form)


@bp.route("/ccpo-users/confirm-new", methods=["POST"])
@user_can(Permissions.CREATE_CCPO_USER, message="create ccpo user")
def confirm_new_user():
    user = Users.get_by_dod_id(request.form["dod_id"])
    Users.give_ccpo_perms(user)
    flash("ccpo_user_added", user_name=user.full_name)
    return redirect(url_for("ccpo.users"))
