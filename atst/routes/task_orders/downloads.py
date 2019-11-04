from flask import Response, current_app as app

from .blueprint import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.exceptions import NotFoundError
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


def send_file(attachment):
    generator = app.csp.files.download(attachment.object_name)
    return Response(
        generator,
        headers={
            "Content-Disposition": "attachment; filename={}".format(attachment.filename)
        },
    )


@task_orders_bp.route("/task_orders/<task_order_id>/pdf")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="download task order PDF")
def download_task_order_pdf(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if task_order.pdf:
        return send_file(task_order.pdf)
    else:
        raise NotFoundError("task_order pdf")
