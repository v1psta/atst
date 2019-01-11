from flask import g, render_template

from . import workspaces_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.workspaces import Workspaces


@workspaces_bp.route("/workspaces/<workspace_id>/task_orders")
def workspace_task_orders(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    return render_template("workspaces/task_orders/index.html", workspace=workspace)


@workspaces_bp.route("/workspaces/<workspace_id>/task_order/<task_order_id>")
def view_task_order(workspace_id, task_order_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    return render_template(
        "workspaces/task_orders/show.html", workspace=workspace, task_order=task_order
    )
