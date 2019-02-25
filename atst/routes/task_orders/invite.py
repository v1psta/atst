from flask import redirect, url_for, g

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.flash import formatted_flash as flash
from atst.services.invitation import update_officer_invitations


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
