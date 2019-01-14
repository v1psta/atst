from flask import g, render_template

from . import portfolios_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolios import Portfolios


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
def portfolio_task_orders(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    return render_template("portfolios/task_orders/index.html", portfolio=portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    return render_template(
        "portfolios/task_orders/show.html", portfolio=portfolio, task_order=task_order
    )
