from flask import url_for, redirect, render_template, g, request as http_request

import datetime

from . import task_orders_bp
from atst.domain.authz import Authorization
from atst.domain.exceptions import NoAccessError
from atst.domain.task_orders import TaskOrders
from atst.forms.task_order import SignatureForm
from atst.utils.flash import formatted_flash as flash
from atst.domain.authz.decorator import user_can_access_decorator as user_can


def find_unsigned_ko_to(task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)

    if not TaskOrders.can_ko_sign(task_order):
        raise NoAccessError("task_order")

    return task_order


def wrap_check_is_ko(user, _perm, task_order_id=None, **_kwargs):
    task_order = TaskOrders.get(user, task_order_id)
    Authorization.check_is_ko(user, task_order)

    return True


@task_orders_bp.route("/task_orders/<task_order_id>/digital_signature", methods=["GET"])
@user_can(None, exceptions=[wrap_check_is_ko])
def signature_requested(task_order_id):
    task_order = find_unsigned_ko_to(task_order_id)

    return render_template(
        "task_orders/signing/signature_requested.html",
        task_order_id=task_order.id,
        portfolio_id=task_order.portfolio_id,
        form=SignatureForm(),
    )


@task_orders_bp.route(
    "/task_orders/<task_order_id>/digital_signature", methods=["POST"]
)
@user_can(None, exceptions=[wrap_check_is_ko])
def record_signature(task_order_id):
    task_order = find_unsigned_ko_to(task_order_id)

    form_data = {**http_request.form}

    if "unlimited_level_of_warrant" in form_data and form_data[
        "unlimited_level_of_warrant"
    ] == ["y"]:
        del form_data["level_of_warrant"]

    form = SignatureForm(form_data)

    if form.validate():
        TaskOrders.update(
            user=g.current_user,
            task_order=task_order,
            signer_dod_id=g.current_user.dod_id,
            signed_at=datetime.datetime.now(),
            **form.data,
        )

        flash("task_order_signed")
        return redirect(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=task_order.portfolio_id,
                task_order_id=task_order.id,
            )
        )
    else:
        return (
            render_template(
                "task_orders/signing/signature_requested.html",
                task_order_id=task_order_id,
                portfolio_id=task_order.portfolio_id,
                form=form,
            ),
            400,
        )
