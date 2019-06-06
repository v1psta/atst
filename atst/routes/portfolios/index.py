from datetime import date, timedelta

from flask import redirect, render_template, url_for, request as http_request, g

from . import portfolios_bp
from atst.forms.portfolio import PortfolioCreationForm
from atst.domain.reports import Reports
from atst.domain.portfolios import Portfolios
from atst.models.permissions import Permissions
from atst.domain.authz.decorator import user_can_access_decorator as user_can


@portfolios_bp.route("/portfolios")
def portfolios():
    portfolios = Portfolios.for_user(g.current_user)

    if portfolios:
        return render_template("portfolios/index.html", page=5, portfolios=portfolios)
    else:
        return render_template("portfolios/blank_slate.html")


@portfolios_bp.route("/portfolios/new")
def new_portfolio():
    form = PortfolioCreationForm()

    return render_template("portfolios/new.html", form=form)


@portfolios_bp.route("/portfolios", methods=["POST"])
def create_portfolio():
    form = PortfolioCreationForm(http_request.form)

    if form.validate():
        portfolio = Portfolios.create(user=g.current_user, portfolio_attrs=form.data)
        return redirect(
            url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        return render_template("portfolios/new.html", form=form), 400


@portfolios_bp.route("/portfolios/<portfolio_id>/reports")
@user_can(Permissions.VIEW_PORTFOLIO_REPORTS, message="view portfolio reports")
def reports(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
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


@portfolios_bp.route("/portfolios/<portfolio_id>/destroy", methods=["POST"])
@user_can(Permissions.ARCHIVE_PORTFOLIO, message="archive portfolio")
def delete_portfolio(portfolio_id):
    Portfolios.delete(portfolio=g.portfolio)

    return redirect(url_for("atst.home"))
