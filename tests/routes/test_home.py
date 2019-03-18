import pytest

from tests.factories import UserFactory, PortfolioFactory
from atst.domain.portfolios import Portfolios
from atst.models.portfolio_role import Status as PortfolioRoleStatus


def test_portfolio_owner_with_one_portfolio_redirected_to_reports(client, user_session):
    portfolio = PortfolioFactory.create()

    user_session(portfolio.owner)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios/{}/reports".format(portfolio.id) in response.location


def test_portfolio_owner_with_more_than_one_portfolio_redirected_to_portfolios(
    client, user_session
):
    owner = UserFactory.create()
    PortfolioFactory.create(owner=owner)
    PortfolioFactory.create(owner=owner)

    user_session(owner)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios" in response.location


def test_non_owner_user_with_one_portfolio_redirected_to_portfolio_applications(
    client, user_session
):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(
        user, portfolio, status=PortfolioRoleStatus.ACTIVE
    )

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios/{}/applications".format(portfolio.id) in response.location


def test_non_owner_user_with_mulitple_portfolios_redirected_to_portfolios(
    client, user_session
):
    user = UserFactory.create()
    portfolios = []
    for _ in range(3):
        portfolio = PortfolioFactory.create()
        portfolios.append(portfolio)
        role = Portfolios._create_portfolio_role(
            user, portfolio, status=PortfolioRoleStatus.ACTIVE
        )

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    alphabetically_first_portfolio = sorted(portfolios, key=lambda p: p.name)[0]
    assert "/portfolios" in response.location
    assert str(alphabetically_first_portfolio.id) in response.location
