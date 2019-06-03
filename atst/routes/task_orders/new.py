from flask import g, render_template, request as http_request

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def new(portfolio_id):
    return render_template("task_orders/new.html", form=TaskOrderForm())


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="create new task order")
def create(portfolio_id):
    form_data = http_request.form
    form = TaskOrderForm(form_data)

    if form.validate():
        TaskOrders.create(g.current_user, portfolio_id, **form.data)
        flash("task_order_draft")
        return render_template("task_orders/new.html", form=form)
    else:
        flash("form_errors")
        return render_template("task_orders/new.html", form=form)


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/<task_order_id>/edit")
@user_can(Permissions.CREATE_TASK_ORDER, message="update task order")
def edit(portfolio_id, taks_order_id):
    return render_template("task_orders/edit", form=TaskOrderForm())


@task_orders_bp.route(
    "/portfolios/<portfolio_id>/task_orders/<task_order_id>", methods=["POST"]
)
@user_can(Permissions.CREATE_TASK_ORDER, message="update task order")
def update(portfolio_id, task_order_id=None):
    form_data = http_request.form
    form = TaskOrderForm(form_data)

    if form.validate():
        TaskOrders.update(task_order_id, **form.data)
        flash("task_order_draft")
        return render_template("task_orders/new.html", form=form)
    else:
        flash("form_errors")
        return render_template("task_orders/new.html", form=form)
