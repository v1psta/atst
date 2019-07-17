from flask import g, redirect, render_template, request as http_request, url_for

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm, SignatureForm
from atst.models.permissions import Permissions


def render_task_orders_edit(template, portfolio_id=None, task_order_id=None, form=None):
    render_args = {}

    if task_order_id:
        task_order = TaskOrders.get(task_order_id)
        portfolio_id = task_order.portfolio_id
        render_args["form"] = form or TaskOrderForm(obj=task_order)
        render_args["task_order_id"] = task_order_id
        render_args["task_order"] = task_order
    else:
        render_args["form"] = form or TaskOrderForm()

    render_args["cancel_url"] = url_for(
        "task_orders.portfolio_funding", portfolio_id=portfolio_id
    )

    return render_template(template, **render_args)


def update_task_order(
    form_data, next_page, current_template, portfolio_id=None, task_order_id=None
):
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

        return redirect(url_for(next_page, task_order_id=task_order.id))
    else:
        return (
            render_task_orders_edit(
                current_template, portfolio_id, task_order_id, form
            ),
            400,
        )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/step_1")
@task_orders_bp.route("/task_orders/<task_order_id>/step_1")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def form_step_one_add_pdf(portfolio_id=None, task_order_id=None):
    return render_task_orders_edit(
        "task_orders/step_1.html",
        portfolio_id=portfolio_id,
        task_order_id=task_order_id,
    )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/step-1", methods=["POST"])
@task_orders_bp.route("/task_orders/<task_order_id>/step_1", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def submit_form_step_one_add_pdf(portfolio_id=None, task_order_id=None):
    form_data = {**http_request.form, **http_request.files}
    next_page = "task_orders.form_step_two_add_number"
    current_template = "task_orders/step_1.html"

    return update_task_order(
        form_data,
        next_page,
        current_template,
        portfolio_id=portfolio_id,
        task_order_id=task_order_id,
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_2")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def form_step_two_add_number(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_2.html", task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_2", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def submit_form_step_two_add_number(task_order_id):
    form_data = {**http_request.form}
    next_page = "task_orders.form_step_three_add_clins"
    current_template = "task_orders/step_2.html"

    return update_task_order(
        form_data, next_page, current_template, task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_3")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def form_step_three_add_clins(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_3.html", task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_3", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def submit_form_step_three_add_clins(task_order_id):
    form_data = {**http_request.form}
    next_page = "task_orders.form_step_four_review"
    current_template = "task_orders/step_3.html"

    return update_task_order(
        form_data, next_page, current_template, task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_4")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def form_step_four_review(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_4.html", task_order_id=task_order_id
    )


@task_orders_bp.route("/task_orders/<task_order_id>/step_5")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def form_step_five_confirm_signature(task_order_id):
    return render_task_orders_edit(
        "task_orders/step_5.html", task_order_id=task_order_id, form=SignatureForm()
    )
