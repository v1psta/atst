from io import BytesIO
from flask import Response, current_app as app

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.exceptions import NotFoundError
from atst.utils.docx import Docx
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


@task_orders_bp.route("/task_orders/download_summary/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS)
def download_summary(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    byte_str = BytesIO()
    Docx.render(byte_str, data=task_order.to_dictionary())
    filename = "{}.docx".format(task_order.portfolio_name)
    return Response(
        byte_str,
        headers={"Content-Disposition": "attachment; filename={}".format(filename)},
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def send_file(attachment):
    generator = app.csp.files.download(attachment.object_name)
    return Response(
        generator,
        headers={
            "Content-Disposition": "attachment; filename={}".format(attachment.filename)
        },
    )


@task_orders_bp.route("/task_orders/csp_estimate/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS)
def download_csp_estimate(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if task_order.csp_estimate:
        return send_file(task_order.csp_estimate)
    else:
        raise NotFoundError("task_order CSP estimate")


@task_orders_bp.route("/task_orders/pdf/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS)
def download_task_order_pdf(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if task_order.pdf:
        return send_file(task_order.pdf)
    else:
        raise NotFoundError("task_order pdf")
