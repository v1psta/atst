from operator import attrgetter

from flask import request as http_request, g
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.authz import Authorization
from atst.models import Application, Environment, Portfolio, TaskOrder
from atst.models.permissions import Permissions
from atst.domain.portfolios.scopes import ScopedPortfolio


def get_portfolio_from_context(view_args):
    query = None

    if "portfolio_id" in view_args:
        query = db.session.query(Portfolio).filter(
            Portfolio.id == view_args["portfolio_id"]
        )

    elif "application_id" in view_args:
        query = (
            db.session.query(Portfolio)
            .join(Application, Application.portfolio_id == Portfolio.id)
            .filter(Application.id == view_args["application_id"])
        )

    elif "environment_id" in view_args:
        query = (
            db.session.query(Portfolio)
            .join(Application, Application.portfolio_id == Portfolio.id)
            .join(Environment, Environment.application_id == Application.id)
            .filter(Environment.id == view_args["environment_id"])
        )

    elif "task_order_id" in view_args:
        query = (
            db.session.query(Portfolio)
            .join(TaskOrder, TaskOrder.portfolio_id == Portfolio.id)
            .filter(TaskOrder.id == view_args["task_order_id"])
        )

    if query:
        try:
            portfolio = query.one()

            return ScopedPortfolio(g.current_user, portfolio)
        except NoResultFound:
            raise NotFoundError("portfolio")


def portfolio():
    portfolio = get_portfolio_from_context(http_request.view_args)

    def user_can(permission):
        if portfolio:
            return Authorization.has_portfolio_permission(
                g.current_user, portfolio, permission
            )
        return False

    if not portfolio is None:
        active_task_orders = [
            task_order for task_order in portfolio.task_orders if task_order.is_active
        ]
        funding_end_date = (
            sorted(active_task_orders, key=attrgetter("end_date"))[-1].end_date
            if active_task_orders
            else None
        )
        funded = len(active_task_orders) > 1
    else:
        funding_end_date = None
        funded = None

    return {
        "portfolio": portfolio,
        "permissions": Permissions,
        "user_can": user_can,
        "funding_end_date": funding_end_date,
        "funded": funded,
    }
