from flask import g, redirect, render_template, url_for, request as http_request

from . import task_orders_bp
from atst.domain.authz import Authorization
from atst.domain.exceptions import NoAccessError
from atst.domain.task_orders import TaskOrders
from atst.forms.dd_254 import DD254Form
from atst.forms.ko_review import KOReviewForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can


def wrap_check_is_ko_or_cor(user, task_order_id=None, **_kwargs):
    task_order = TaskOrders.get(task_order_id)
    Authorization.check_is_ko_or_cor(user, task_order)

    return True


@task_orders_bp.route("/task_orders/<task_order_id>/review")
@user_can(
    None,
    override=wrap_check_is_ko_or_cor,
    message="view contracting officer review form",
)
def ko_review(task_order_id):
    task_order = TaskOrders.get(task_order_id)

    if TaskOrders.all_sections_complete(task_order):
        return render_template(
            "/portfolios/task_orders/review.html",
            task_order=task_order,
            form=KOReviewForm(obj=task_order),
        )
    else:
        raise NoAccessError("task_order")


@task_orders_bp.route("/task_orders/<task_order_id>/review", methods=["POST"])
@user_can(
    None, override=wrap_check_is_ko_or_cor, message="submit contracting officer review"
)
def submit_ko_review(task_order_id, form=None):
    task_order = TaskOrders.get(task_order_id)
    form_data = {**http_request.form, **http_request.files}
    form = KOReviewForm(form_data)

    if form.validate():
        TaskOrders.update(task_order=task_order, **form.data)
        if Authorization.is_ko(g.current_user, task_order) and TaskOrders.can_ko_sign(
            task_order
        ):
            return redirect(
                url_for("task_orders.signature_requested", task_order_id=task_order_id)
            )
        else:
            return redirect(
                url_for("task_orders.view_task_order", task_order_id=task_order_id)
            )
    else:
        return render_template(
            "/portfolios/task_orders/review.html", task_order=task_order, form=form
        )


def so_review_form(task_order):
    if task_order.dd_254:
        dd_254 = task_order.dd_254
        form = DD254Form(obj=dd_254)
        form.required_distribution.data = dd_254.required_distribution
        return form
    else:
        so = task_order.officer_dictionary("security_officer")
        form_data = {
            "certifying_official": "{}, {}".format(
                so.get("last_name", ""), so.get("first_name", "")
            ),
            "co_phone": so.get("phone_number", ""),
        }
        return DD254Form(data=form_data)


def wrap_check_is_so(user, task_order_id=None, **_kwargs):
    task_order = TaskOrders.get(task_order_id)
    Authorization.check_is_so(user, task_order)

    return True


@task_orders_bp.route("/task_orders/<task_order_id>/dd254")
@user_can(None, override=wrap_check_is_so, message="view security officer review form")
def so_review(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = so_review_form(task_order)

    return render_template(
        "portfolios/task_orders/so_review.html", form=form, task_order=task_order
    )


@task_orders_bp.route("/task_orders/<task_order_id>/dd254", methods=["POST"])
@user_can(
    None, override=wrap_check_is_so, message="submit security officer review form"
)
def submit_so_review(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = DD254Form(http_request.form)

    if form.validate():
        TaskOrders.add_dd_254(task_order, form.data)
        # TODO: will redirect to download, sign, upload page
        return redirect(
            url_for("task_orders.view_task_order", task_order_id=task_order.id)
        )
    else:
        return render_template(
            "portfolios/task_orders/so_review.html", form=form, task_order=task_order
        )
