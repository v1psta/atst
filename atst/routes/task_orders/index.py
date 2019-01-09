from io import BytesIO
from flask import g, Response

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.utils.docx import Docx


@task_orders_bp.route("/task_orders/download_summary/<task_order_id>")
def download_summary(task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    byte_str = BytesIO()
    Docx.render(byte_str, data=task_order.to_dictionary())
    filename = "{}.docx".format(task_order.portfolio_name)
    return Response(
        byte_str,
        headers={"Content-Disposition": "attachment; filename={}".format(filename)},
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
