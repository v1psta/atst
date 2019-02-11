from flask import redirect, url_for, g

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.flash import formatted_flash as flash
from atst.domain.portfolio_roles import PortfolioRoles
from atst.services.invitation import Invitation as InvitationService


OFFICER_INVITATIONS = [
    {
        "field": "ko_invite",
        "role": "contracting_officer",
        "subject": "Review a task order",
        "template": "emails/invitation.txt",
    },
    {
        "field": "cor_invite",
        "role": "contracting_officer_representative",
        "subject": "Help with a task order",
        "template": "emails/invitation.txt",
    },
    {
        "field": "so_invite",
        "role": "security_officer",
        "subject": "Review security for a task order",
        "template": "emails/invitation.txt",
    },
]


def update_officer_invitations(user, task_order):
    for officer_type in OFFICER_INVITATIONS:
        field = officer_type["field"]
        if getattr(task_order, field) and not getattr(task_order, officer_type["role"]):
            officer_data = task_order.officer_dictionary(officer_type["role"])
            officer = TaskOrders.add_officer(
                user, task_order, officer_type["role"], officer_data
            )
            pf_officer_member = PortfolioRoles.get(task_order.portfolio.id, officer.id)
            invite_service = InvitationService(
                user,
                pf_officer_member,
                officer_data["email"],
                subject=officer_type["subject"],
                email_template=officer_type["template"],
            )
            invite_service.invite()


@task_orders_bp.route("/task_orders/invite/<task_order_id>", methods=["POST"])
def invite(task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    if TaskOrders.all_sections_complete(task_order):
        update_officer_invitations(g.current_user, task_order)

        portfolio = task_order.portfolio
        flash("task_order_congrats", portfolio=portfolio)
        return redirect(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=task_order.portfolio_id,
                task_order_id=task_order.id,
            )
        )
    else:
        flash("task_order_incomplete")
        return redirect(
            url_for("task_orders.new", screen=4, task_order_id=task_order.id)
        )
