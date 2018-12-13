from flask import Blueprint, request as http_request, render_template

from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import TaskOrderForm

task_orders_bp = Blueprint("task_orders", __name__)


@task_orders_bp.route("/task_order/edit/<task_order_id>")
def edit(task_order_id):
    form = TaskOrderForm()
    task_order = TaskOrders.get(task_order_id)
    return render_template("task_orders/edit.html", form=form, task_order=task_order)


@task_orders_bp.route("/task_order/edit/<task_order_id>", methods=["POST"])
def update(task_order_id):
    form = TaskOrderForm(http_request.form)
    task_order = TaskOrders.get(task_order_id)
    if form.validate():
        TaskOrders.update(task_order, **form.data)
        return "i did it"
    else:
        return render_template(
            "task_orders/edit.html", form=form, task_order=task_order
        )
