from flask import g, redirect, url_for, render_template, request as http_request

from . import workspaces_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.workspaces import Workspaces
from atst.forms.workspace import WorkspaceForm


@workspaces_bp.route("/workspaces/new")
def new():
    form = WorkspaceForm()
    return render_template("workspaces/new.html", form=form)


@workspaces_bp.route("/workspaces/new", methods=["POST"])
def create():
    form = WorkspaceForm(http_request.form)
    if form.validate():
        ws = Workspaces.create(g.current_user, form.name.data)
        task_order = TaskOrders.create(workspace=ws, creator=g.current_user)
        return redirect(url_for("task_orders.edit", task_order_id=task_order.id))
    else:
        return render_template("workspaces/new.html", form=form)
