from flask import g, redirect, url_for, render_template

from . import portfolios_bp
from atst.domain.invitations import Invitations
from atst.queue import queue
from atst.utils.flash import formatted_flash as flash
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


def send_invite_email(owner_name, token, new_member_email):
    body = render_template("emails/invitation.txt", owner=owner_name, token=token)
    queue.send_mail(
        [new_member_email],
        "{} has invited you to a JEDI Cloud Portfolio".format(owner_name),
        body,
    )


@portfolios_bp.route("/portfolios/invitations/<token>", methods=["GET"])
def accept_invitation(token):
    invite = Invitations.accept(g.current_user, token)

    for task_order in invite.portfolio.task_orders:
        if g.current_user in task_order.officers:
            return redirect(
                url_for("task_orders.view_task_order", task_order_id=task_order.id)
            )

    return redirect(
        url_for("portfolios.show_portfolio", portfolio_id=invite.portfolio.id)
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/invitations/<token>/revoke", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="revoke invitation")
def revoke_invitation(portfolio_id, token):
    Invitations.revoke(token)

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            _anchor="portfolio-members",
            fragment="portfolio-members",
        )
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/invitations/<token>/resend", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="resend invitation")
def resend_invitation(portfolio_id, token):
    invite = Invitations.resend(g.current_user, token)
    send_invite_email(g.current_user.full_name, invite.token, invite.email)
    flash("resend_portfolio_invitation", user_name=invite.user_name)
    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            fragment="portfolio-members",
            _anchor="portfolio-members",
        )
    )
