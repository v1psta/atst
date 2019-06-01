from copy import deepcopy

from flask import (
    g,
    redirect,
    render_template,
    request as http_request,
    url_for,
)

from . import task_orders_bp
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash
from atst.utils.localization import translate


@task_orders_bp.route("/task_orders/new/get_started")
# TODO: see if this route still exists in new design
def get_started():
    return render_template("task_orders/new/get_started.html")  # pragma: no cover


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new")
@user_can(Permissions.CREATE_TASK_ORDER, message="view new task order form")
def new(portfolio_id):
    return render_template("task_orders/new", form=TaskOrderForm())


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new", methods=["POST"])
@user_can(Permissions.CREATE_TASK_ORDER, message="create new task order")
def create(portfolio_id):
    form_data = http_request.form
    form = TaskOrderForm(form_data)

    if form.validate():
        TaskOrders.create(g.current_user, portfolio_id, **form.data)
    # TODO: ask UX where do you go after save


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
    # TODO: ask UX where do you go after save
