from collections import defaultdict
from operator import itemgetter

from flask import g, redirect, render_template, url_for, request as http_request

from . import portfolios_bp
from atst.database import db
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from atst.forms.officers import EditTaskOrderOfficersForm
from atst.models.task_order import Status as TaskOrderStatus
from atst.forms.ko_review import KOReviewForm


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders_by_status = defaultdict(list)
    serialize_task_order = lambda task_order: {
        key: getattr(task_order, key)
        for key in [
            "id",
            "budget",
            "time_created",
            "start_date",
            "end_date",
            "display_status",
            "balance",
        ]
    }

    for task_order in portfolio.task_orders:
        serialized_task_order = serialize_task_order(task_order)
        serialized_task_order["url"] = url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
        task_orders_by_status[task_order.status].append(serialized_task_order)

    active_task_orders = task_orders_by_status.get(TaskOrderStatus.ACTIVE, [])
    funding_end_date = (
        sorted(active_task_orders, key=itemgetter("end_date"))[-1]["end_date"]
        if active_task_orders
        else None
    )
    total_balance = sum([task_order["balance"] for task_order in active_task_orders])

    return render_template(
        "portfolios/task_orders/index.html",
        portfolio=portfolio,
        pending_task_orders=task_orders_by_status.get(TaskOrderStatus.PENDING, []),
        active_task_orders=active_task_orders,
        expired_task_orders=task_orders_by_status.get(TaskOrderStatus.EXPIRED, []),
        funding_end_date=funding_end_date,
        total_balance=total_balance,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    completed = TaskOrders.all_sections_complete(task_order)
    return render_template(
        "portfolios/task_orders/show.html",
        portfolio=portfolio,
        task_order=task_order,
        all_sections_complete=completed,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>/review")
def ko_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    if not Authorization.is_ko(g.current_user, task_order):
        message = "review Task Order {}".format(task_order.id)
        raise UnauthorizedError(g.current_user, message)
    else:
        return render_template(
            "/portfolios/task_orders/review.html",
            portfolio=portfolio,
            task_order=task_order,
            form=KOReviewForm(obj=task_order),
        )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/review", methods=["POST"]
)
def submit_ko_review(portfolio_id, task_order_id, form=None):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form = KOReviewForm(http_request.form)
    portfolio = Portfolios.get(g.current_user, portfolio_id)

    if form.validate():
        TaskOrders.update(user=g.current_user, task_order=task_order, **form.data)
        return redirect(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=portfolio_id,
                task_order_id=task_order_id,
            )
        )
    else:
        return render_template(
            "/portfolios/task_orders/review.html",
            portfolio=portfolio,
            task_order=task_order,
            form=form,
        )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations"
)
def task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form = EditTaskOrderOfficersForm(obj=task_order)
    return render_template(
        "portfolios/task_orders/invitations.html",
        portfolio=portfolio,
        task_order=task_order,
        form=form,
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations",
    methods=["POST"],
)
def edit_task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form = EditTaskOrderOfficersForm(formdata=http_request.form, obj=task_order)

    if form.validate():
        form.populate_obj(task_order)
        db.session.add(task_order)
        db.session.commit()

        return redirect(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=portfolio.id,
                task_order_id=task_order.id,
            )
        )
    else:
        return render_template(
            "portfolios/task_orders/invitations.html",
            portfolio=portfolio,
            task_order=task_order,
            form=form,
        )
