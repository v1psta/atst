from flask import g, redirect, render_template, url_for, request as http_request

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.flash import formatted_flash as flash
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.database import db
from atst.domain.exceptions import NotFoundError, NoAccessError
from atst.domain.invitations import PortfolioInvitations
from atst.domain.portfolios import Portfolios
from atst.utils.localization import translate
from atst.forms.officers import EditTaskOrderOfficersForm
from atst.services.invitation import (
    update_officer_invitations,
    OFFICER_INVITATIONS,
    Invitation as InvitationService,
)


@task_orders_bp.route("/task_orders/<task_order_id>/invite", methods=["POST"])
@user_can(Permissions.EDIT_TASK_ORDER_DETAILS, message="invite task order officers")
def invite(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if TaskOrders.all_sections_complete(task_order):
        update_officer_invitations(g.current_user, task_order)

        portfolio = task_order.portfolio
        flash("task_order_congrats", portfolio=portfolio)
        return redirect(
            url_for("task_orders.view_task_order", task_order_id=task_order.id)
        )
    else:
        flash("task_order_incomplete")
        return redirect(
            url_for("task_orders.new", screen=4, task_order_id=task_order.id)
        )


@task_orders_bp.route("/task_orders/<task_order_id>/resend_invite", methods=["POST"])
@user_can(
    Permissions.EDIT_TASK_ORDER_DETAILS, message="resend task order officer invites"
)
def resend_invite(task_order_id):
    invite_type = http_request.args.get("invite_type")

    if invite_type not in OFFICER_INVITATIONS:
        raise NotFoundError("invite_type")

    invite_type_info = OFFICER_INVITATIONS[invite_type]

    task_order = TaskOrders.get(task_order_id)
    portfolio = Portfolios.get(g.current_user, task_order.portfolio_id)

    officer = getattr(task_order, invite_type_info["role"])

    if not officer:
        raise NotFoundError("officer")

    invitation = PortfolioInvitations.lookup_by_portfolio_and_user(portfolio, officer)

    if not invitation:
        raise NotFoundError("invitation")

    if not invitation.can_resend:
        raise NoAccessError("invitation")

    PortfolioInvitations.revoke(token=invitation.token)

    invite_service = InvitationService(
        g.current_user,
        invitation.role,
        invitation.email,
        subject=invite_type_info["subject"],
        email_template=invite_type_info["template"],
    )

    invite_service.invite()

    flash(
        "invitation_resent",
        officer_type=translate(
            "common.officer_helpers.underscore_to_friendly.{}".format(
                invite_type_info["role"]
            )
        ),
    )

    return redirect(url_for("task_orders.invitations", task_order_id=task_order_id))


@task_orders_bp.route("/task_orders/<task_order_id>/invitations")
@user_can(
    Permissions.EDIT_TASK_ORDER_DETAILS, message="view task order invitations page"
)
def invitations(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = EditTaskOrderOfficersForm(obj=task_order)

    if TaskOrders.all_sections_complete(task_order):
        return render_template(
            "portfolios/task_orders/invitations.html",
            task_order=task_order,
            form=form,
            user=g.current_user,
        )
    else:
        raise NotFoundError("task_order")


@task_orders_bp.route("/task_orders/<task_order_id>/invitations/edit", methods=["POST"])
@user_can(Permissions.EDIT_TASK_ORDER_DETAILS, message="edit task order invitations")
def invitations_edit(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = EditTaskOrderOfficersForm(formdata=http_request.form, obj=task_order)

    if form.validate():
        form.populate_obj(task_order)
        db.session.add(task_order)
        db.session.commit()
        update_officer_invitations(g.current_user, task_order)

        return redirect(url_for("task_orders.invitations", task_order_id=task_order.id))
    else:
        return (
            render_template(
                "portfolios/task_orders/invitations.html",
                task_order=task_order,
                form=form,
            ),
            400,
        )
