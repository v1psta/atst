import pytest

from tests.factories import UserFactory, PortfolioFactory, RequestFactory
from atst.domain.portfolios import Portfolios


def test_request_owner_with_one_portfolio_redirected_to_reports(client, user_session):
    request = RequestFactory.create()
    portfolio = Portfolios.create_from_request(request)

    user_session(request.creator)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios/{}/reports".format(portfolio.id) in response.location


def test_request_owner_with_more_than_one_portfolio_redirected_to_portfolios(
    client, user_session
):
    request_creator = UserFactory.create()
    Portfolios.create_from_request(RequestFactory.create(creator=request_creator))
    Portfolios.create_from_request(RequestFactory.create(creator=request_creator))

    user_session(request_creator)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios" in response.location


def test_non_owner_user_with_one_portfolio_redirected_to_portfolio_applications(
    client, user_session
):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios/{}/applications".format(portfolio.id) in response.location


def test_non_owner_user_with_mulitple_portfolios_redirected_to_portfolios(
    client, user_session
):
    user = UserFactory.create()
    for _ in range(3):
        portfolio = PortfolioFactory.create()
        Portfolios._create_portfolio_role(user, portfolio, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/portfolios" in response.location


@pytest.mark.skip(reason="this may no longer be accurate")
def test_ccpo_user_redirected_to_requests(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    for _ in range(3):
        portfolio = PortfolioFactory.create()
        Portfolios._create_portfolio_role(user, portfolio, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/requests" in response.location
