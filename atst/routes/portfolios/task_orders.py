from collections import defaultdict

from flask import g, render_template

from . import portfolios_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolios import Portfolios
from atst.models.task_order import Status as TaskOrderStatus


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
def portfolio_task_orders(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders_by_status = defaultdict(list)
    for task_order in portfolio.task_orders:
        task_orders_by_status[task_order.status].append(task_order)

    return render_template(
        "portfolios/task_orders/index.html",
        portfolio=portfolio,
        pending_task_orders=task_orders_by_status.get(TaskOrderStatus.PENDING, []),
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    return render_template(
        "portfolios/task_orders/show.html", portfolio=portfolio, task_order=task_order
    )
