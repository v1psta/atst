from flask import redirect, url_for, g

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.flash import formatted_flash as flash


@task_orders_bp.route("/task_orders/invite/<task_order_id>", methods=["POST"])
def invite(task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    portfolio = task_order.portfolio
    flash("task_order_congrats", portfolio=portfolio)
    return redirect(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=task_order.portfolio_id,
            task_order_id=task_order.id,
        )
    )
