from flask import g, redirect, render_template, request as http_request, url_for

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def render_task_orders_edit(portfolio_id=None, task_order_id=None, form=None):
    render_args = {}

    if task_order_id:
        task_order = TaskOrders.get(task_order_id)
        portfolio_id = task_order.portfolio_id
        render_args["form"] = form or TaskOrderForm(**task_order.to_dictionary())
        render_args["task_order_id"] = task_order_id
        render_args["task_order"] = task_order
    else:
        render_args["form"] = form or TaskOrderForm()

    render_args["cancel_url"] = (
        http_request.referrer
        if http_request.referrer
        else url_for("task_orders.portfolio_funding", portfolio_id=portfolio_id)
    )

    return render_template("task_orders/edit.html", **render_args)


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new")
@task_orders_bp.route("/task_orders/<task_order_id>/edit")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def edit(portfolio_id=None, task_order_id=None):
    return render_task_orders_edit(portfolio_id, task_order_id)


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new", methods=["POST"])
@task_orders_bp.route("/task_orders/<task_order_id>", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="create new task order")
def update(portfolio_id=None, task_order_id=None):
    form_data = {**http_request.form, **http_request.files}

    form = None
    if task_order_id:
        task_order = TaskOrders.get(task_order_id)
        form = TaskOrderForm(form_data, obj=task_order)
    else:
        form = TaskOrderForm(form_data)

    if form.validate():
        task_order = None
        if task_order_id:
            task_order = TaskOrders.update(task_order_id, **form.data)
            portfolio_id = task_order.portfolio_id
        else:
            task_order = TaskOrders.create(g.current_user, portfolio_id, **form.data)

        if http_request.args.get("review"):
            return redirect(
                url_for("task_orders.review_task_order", task_order_id=task_order.id)
            )

        flash("task_order_draft")

        return redirect(url_for("task_orders.edit", task_order_id=task_order.id))
    else:
        flash("form_errors")
        return render_task_orders_edit(portfolio_id, task_order_id, form), 400
