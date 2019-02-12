from datetime import date, timedelta

from flask import render_template, request as http_request, g, redirect, url_for

from . import portfolios_bp
from atst.domain.reports import Reports
from atst.domain.portfolios import Portfolios
from atst.domain.audit_log import AuditLog
from atst.domain.authz import Authorization
from atst.domain.common import Paginator
from atst.forms.portfolio import PortfolioForm
from atst.models.permissions import Permissions


@portfolios_bp.route("/portfolios")
def portfolios():
    portfolios = Portfolios.for_user(g.current_user)
    return render_template("portfolios/index.html", page=5, portfolios=portfolios)


@portfolios_bp.route("/portfolios/<portfolio_id>/admin")
def portfolio(portfolio_id):
    portfolio = Portfolios.get_for_update_information(g.current_user, portfolio_id)
    form = PortfolioForm(data={"name": portfolio.name})
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_portfolio_events(
        g.current_user, portfolio, pagination_opts
    )
    return render_template(
        "portfolios/admin.html",
        form=form,
        portfolio=portfolio,
        portfolio_name=portfolio.name,
        portfolio_id=portfolio_id,
        audit_events=audit_events,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/edit", methods=["POST"])
def edit_portfolio(portfolio_id):
    portfolio = Portfolios.get_for_update_information(g.current_user, portfolio_id)
    form = PortfolioForm(http_request.form)
    if form.validate():
        Portfolios.update(portfolio, form.data)
        return redirect(
            url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        return render_template("portfolios/edit.html", form=form, portfolio=portfolio)


@portfolios_bp.route("/portfolios/<portfolio_id>")
def show_portfolio(portfolio_id):
    return redirect(
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/reports")
def portfolio_reports(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    Authorization.check_portfolio_permission(
        g.current_user,
        portfolio,
        Permissions.VIEW_USAGE_DOLLARS,
        "view portfolio reports",
    )

    today = date.today()
    month = http_request.args.get("month", today.month)
    year = http_request.args.get("year", today.year)
    current_month = date(int(year), int(month), 15)
    prev_month = current_month - timedelta(days=28)
    two_months_ago = prev_month - timedelta(days=28)

    task_order = next(
        (task_order for task_order in portfolio.task_orders if task_order.is_active),
        None,
    )
    expiration_date = task_order and task_order.end_date
    if expiration_date:
        remaining_difference = expiration_date - today
        remaining_days = remaining_difference.days
    else:
        remaining_days = None

    return render_template(
        "portfolios/reports/index.html",
        cumulative_budget=Reports.cumulative_budget(portfolio),
        portfolio_totals=Reports.portfolio_totals(portfolio),
        monthly_totals=Reports.monthly_totals(portfolio),
        task_order=task_order,
        current_month=current_month,
        prev_month=prev_month,
        two_months_ago=two_months_ago,
        expiration_date=expiration_date,
        remaining_days=remaining_days,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/activity")
def portfolio_activity(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_portfolio_events(
        g.current_user, portfolio, pagination_opts
    )

    return render_template(
        "portfolios/activity/index.html",
        portfolio_name=portfolio.name,
        portfolio_id=portfolio_id,
        audit_events=audit_events,
    )
