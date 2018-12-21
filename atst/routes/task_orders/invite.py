from flask import redirect, url_for

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.flash import formatted_flash as flash


# TODO: add a real implementation for this
@task_orders_bp.route("/task_orders/invite/<task_order_id>", methods=["POST"])
def invite(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    flash("task_order_submitted", task_order=task_order)
    return redirect(
        url_for("workspaces.workspace_members", workspace_id=task_order.workspace.id)
    )
