from flask import g, render_template, url_for, redirect

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm, SignatureForm
from atst.models import Permissions
from atst.models.task_order import Status as TaskOrderStatus
from atst.utils.flash import formatted_flash as flash


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
    to_form = TaskOrderForm(number=task_order.number)
    signature_form = SignatureForm()
    return render_template(
        "portfolios/task_orders/review.html",
        task_order=task_order,
        to_form=to_form,
        signature_form=signature_form,
    )


@task_orders_bp.route("/task_orders/<task_order_id>/submit", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, "submit task order")
def submit_task_order(task_order_id):

    task_order = TaskOrders.get(task_order_id)
    TaskOrders.sign(task_order=task_order, signer_dod_id=g.current_user.dod_id)

    flash("task_order_submitted", task_order=task_order)

    return redirect(
        url_for("task_orders.portfolio_funding", portfolio_id=task_order.portfolio.id)
    )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders")
@user_can(Permissions.VIEW_PORTFOLIO_FUNDING, message="view portfolio funding")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders = TaskOrders.sort(portfolio.task_orders)
    label_colors = {
        TaskOrderStatus.DRAFT: "warning",
        TaskOrderStatus.ACTIVE: "success",
        TaskOrderStatus.UPCOMING: "info",
        TaskOrderStatus.EXPIRED: "error",
        TaskOrderStatus.UNSIGNED: "purple",
    }
    return render_template(
        "portfolios/task_orders/index.html",
        task_orders=task_orders,
        label_colors=label_colors,
    )
