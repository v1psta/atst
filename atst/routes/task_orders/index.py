from io import BytesIO
from flask import g, Response, current_app as app

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.exceptions import NotFoundError
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


@task_orders_bp.route("/task_orders/csp_estimate/<task_order_id>")
def download_csp_estimate(task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    if task_order.csp_estimate:
        estimate = task_order.csp_estimate
        generator = app.csp.files.download(estimate.object_name)
        return Response(
            generator,
            headers={
                "Content-Disposition": "attachment; filename={}".format(
                    estimate.filename
                )
            },
        )

    else:
        raise NotFoundError("task_order CSP estimate")
