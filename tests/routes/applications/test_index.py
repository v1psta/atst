from flask import url_for, get_flashed_messages

from tests.factories import (
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    EnvironmentRoleFactory,
    EnvironmentFactory,
    ApplicationFactory,
)

from atst.domain.applications import Applications
from atst.domain.portfolios import Portfolios
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.utils import captured_templates


def test_user_with_permission_has_budget_report_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
        in response.data.decode()
    )


def test_user_without_permission_has_no_budget_report_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(
        user, portfolio, status=PortfolioRoleStatus.ACTIVE
    )
    user_session(user)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
        not in response.data.decode()
    )


def test_user_with_permission_has_add_application_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("applications.create", portfolio_id=portfolio.id)
        in response.data.decode()
    )


def test_user_without_permission_has_no_add_application_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio)
    user_session(user)
    response = client.get(
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("applications.create", portfolio_id=portfolio.id)
        not in response.data.decode()
    )