from collections import defaultdict

from flask import g, redirect, render_template, url_for, request as http_request

from . import portfolios_bp
from atst.database import db
from atst.domain.authz import Authorization
from atst.domain.exceptions import NotFoundError, NoAccessError
from atst.domain.invitations import Invitations
from atst.domain.portfolios import Portfolios
from atst.domain.task_orders import TaskOrders, DD254s
from atst.utils.localization import translate
from atst.forms.dd_254 import DD254Form
from atst.forms.ko_review import KOReviewForm
from atst.forms.officers import EditTaskOrderOfficersForm
from atst.models.task_order import Status as TaskOrderStatus
from atst.utils.flash import formatted_flash as flash
from atst.services.invitation import (
    update_officer_invitations,
    OFFICER_INVITATIONS,
    Invitation as InvitationService,
)
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
@user_can(Permissions.VIEW_PORTFOLIO_FUNDING)
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
            "days_to_expiration",
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
    total_balance = sum([task_order["balance"] for task_order in active_task_orders])

    return render_template(
        "portfolios/task_orders/index.html",
        portfolio=portfolio,
        pending_task_orders=(
            task_orders_by_status.get(TaskOrderStatus.STARTED, [])
            + task_orders_by_status.get(TaskOrderStatus.PENDING, [])
        ),
        active_task_orders=active_task_orders,
        expired_task_orders=task_orders_by_status.get(TaskOrderStatus.EXPIRED, []),
        total_balance=total_balance,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS)
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(task_order_id)
    to_form_complete = TaskOrders.all_sections_complete(task_order)
    dd_254_complete = DD254s.is_complete(task_order.dd_254)
    return render_template(
        "portfolios/task_orders/show.html",
        dd_254_complete=dd_254_complete,
        is_cor=Authorization.is_cor(g.current_user, task_order),
        is_ko=Authorization.is_ko(g.current_user, task_order),
        is_so=Authorization.is_so(g.current_user, task_order),
        is_to_signed=TaskOrders.is_signed_by_ko(task_order),
        portfolio=portfolio,
        task_order=task_order,
        to_form_complete=to_form_complete,
        user=g.current_user,
    )


def wrap_check_is_ko_or_cor(user, _perm, task_order_id=None, **_kwargs):
    task_order = TaskOrders.get(task_order_id)
    Authorization.check_is_ko_or_cor(user, task_order)

    return True


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>/review")
@user_can(None, exceptions=[wrap_check_is_ko_or_cor])
def ko_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(task_order_id)
    portfolio = Portfolios.get(g.current_user, portfolio_id)

    if TaskOrders.all_sections_complete(task_order):
        return render_template(
            "/portfolios/task_orders/review.html",
            portfolio=portfolio,
            task_order=task_order,
            form=KOReviewForm(obj=task_order),
        )
    else:
        raise NoAccessError("task_order")


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/resend_invite",
    methods=["POST"],
)
@user_can(Permissions.EDIT_TASK_ORDER_DETAILS)
def resend_invite(portfolio_id, task_order_id):
    invite_type = http_request.args.get("invite_type")

    if invite_type not in OFFICER_INVITATIONS:
        raise NotFoundError("invite_type")

    invite_type_info = OFFICER_INVITATIONS[invite_type]

    task_order = TaskOrders.get(task_order_id)
    portfolio = Portfolios.get(g.current_user, portfolio_id)

    officer = getattr(task_order, invite_type_info["role"])

    if not officer:
        raise NotFoundError("officer")

    invitation = Invitations.lookup_by_portfolio_and_user(portfolio, officer)

    if not invitation:
        raise NotFoundError("invitation")

    if not invitation.can_resend:
        raise NoAccessError("invitation")

    Invitations.revoke(token=invitation.token)

    invite_service = InvitationService(
        g.current_user,
        invitation.portfolio_role,
        invitation.email,
        subject=invite_type_info["subject"],
        email_template=invite_type_info["template"],
    )

    invite_service.invite()

    flash(
        "invitation_resent",
        officer_type=translate(
            "common.officer_helpers.underscore_to_friendly.{}".format(
                invite_type_info["role"]
            )
        ),
    )

    return redirect(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/review", methods=["POST"]
)
@user_can(None, exceptions=[wrap_check_is_ko_or_cor])
def submit_ko_review(portfolio_id, task_order_id, form=None):
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
                url_for(
                    "portfolios.view_task_order",
                    task_order_id=task_order_id,
                    portfolio_id=portfolio_id,
                )
            )
    else:
        return render_template(
            "/portfolios/task_orders/review.html",
            portfolio=Portfolios.get(g.current_user, portfolio_id),
            task_order=task_order,
            form=form,
        )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations"
)
@user_can(Permissions.EDIT_TASK_ORDER_DETAILS)
def task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(task_order_id)
    form = EditTaskOrderOfficersForm(obj=task_order)

    if TaskOrders.all_sections_complete(task_order):
        return render_template(
            "portfolios/task_orders/invitations.html",
            portfolio=portfolio,
            task_order=task_order,
            form=form,
        )
    else:
        raise NotFoundError("task_order")


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations",
    methods=["POST"],
)
@user_can(Permissions.EDIT_TASK_ORDER_DETAILS)
def edit_task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(task_order_id)
    form = EditTaskOrderOfficersForm(formdata=http_request.form, obj=task_order)

    if form.validate():
        form.populate_obj(task_order)
        db.session.add(task_order)
        db.session.commit()
        update_officer_invitations(g.current_user, task_order)

        return redirect(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=portfolio.id,
                task_order_id=task_order.id,
            )
        )
    else:
        return (
            render_template(
                "portfolios/task_orders/invitations.html",
                portfolio=portfolio,
                task_order=task_order,
                form=form,
            ),
            400,
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


def wrap_check_is_so(user, _perm, task_order_id=None, **_kwargs):
    task_order = TaskOrders.get(task_order_id)
    Authorization.check_is_so(user, task_order)

    return True


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>/dd254")
@user_can(None, exceptions=[wrap_check_is_so])
def so_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = so_review_form(task_order)

    return render_template(
        "portfolios/task_orders/so_review.html",
        form=form,
        portfolio=task_order.portfolio,
        task_order=task_order,
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/dd254", methods=["POST"]
)
@user_can(None, exceptions=[wrap_check_is_so])
def submit_so_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(task_order_id)
    form = DD254Form(http_request.form)

    if form.validate():
        TaskOrders.add_dd_254(task_order, form.data)
        # TODO: will redirect to download, sign, upload page
        return redirect(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=task_order.portfolio.id,
                task_order_id=task_order.id,
            )
        )
    else:
        return render_template(
            "portfolios/task_orders/so_review.html",
            form=form,
            portfolio=task_order.portfolio,
            task_order=task_order,
        )
