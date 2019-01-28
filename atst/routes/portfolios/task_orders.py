from collections import defaultdict
from operator import itemgetter

from flask import g, render_template, url_for

from . import portfolios_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolios import Portfolios
from atst.models.task_order import Status as TaskOrderStatus


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders_by_status = defaultdict(list)
    serialize_task_order = lambda task_order: {
        key: getattr(task_order, key)
        for key in [
            "id",
            "budget",
            "time_created",
            "start_date",
            "end_date",
            "display_status",
            "days_to_expiration",
            "balance",
        ]
    }

    for task_order in portfolio.task_orders:
        serialized_task_order = serialize_task_order(task_order)
        serialized_task_order["url"] = url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
        task_orders_by_status[task_order.status].append(serialized_task_order)

    active_task_orders = task_orders_by_status.get(TaskOrderStatus.ACTIVE, [])
    funding_end_date = (
        sorted(active_task_orders, key=itemgetter("end_date"))[-1]["end_date"]
        if active_task_orders
        else None
    )
    total_balance = sum([task_order["balance"] for task_order in active_task_orders])

    return render_template(
        "portfolios/task_orders/index.html",
        portfolio=portfolio,
        pending_task_orders=task_orders_by_status.get(TaskOrderStatus.PENDING, []),
        active_task_orders=active_task_orders,
        expired_task_orders=task_orders_by_status.get(TaskOrderStatus.EXPIRED, []),
        funding_end_date=funding_end_date,
        total_balance=total_balance,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    return render_template(
        "portfolios/task_orders/show.html", portfolio=portfolio, task_order=task_order
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations"
)
def task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    return render_template(
        "portfolios/task_orders/invitations.html",
        portfolio=portfolio,
        task_order=task_order,
    )
