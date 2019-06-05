from collections import defaultdict

from flask import g, render_template, url_for

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.models import Permissions
from atst.models.task_order import Status as TaskOrderStatus


@task_orders_bp.route("/task_orders/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="view task order details")
def view_task_order(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    to_form_complete = TaskOrders.all_sections_complete(task_order)
    return render_template(
        "portfolios/task_orders/show.html",
        task_order=task_order,
        to_form_complete=to_form_complete,
        user=g.current_user,
    )


@task_orders_bp.route("/task_orders/<task_order_id>/review")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="review task order details")
def review_task_order(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    return render_template("portfolios/task_orders/review.html", task_order=task_order)


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders")
@user_can(Permissions.VIEW_PORTFOLIO_FUNDING, message="view portfolio funding")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders_by_status = defaultdict(list)

    for task_order in portfolio.task_orders:
        task_orders_by_status[task_order.status].append(task_order)

    active_task_orders = task_orders_by_status.get(TaskOrderStatus.ACTIVE, [])

    return render_template(
        "portfolios/task_orders/index.html",
        pending_task_orders=(
            task_orders_by_status.get(TaskOrderStatus.STARTED, [])
            + task_orders_by_status.get(TaskOrderStatus.PENDING, [])
        ),
        active_task_orders=active_task_orders,
        expired_task_orders=task_orders_by_status.get(TaskOrderStatus.EXPIRED, []),
    )
