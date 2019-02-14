from flask import url_for

from tests.factories import PortfolioFactory, UserFactory
from atst.utils.localization import translate


def test_update_portfolio_name(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.edit_portfolio", portfolio_id=portfolio.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert portfolio.name == "a cool new name"


def test_portfolio_index_with_existing_portfolios(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)

    response = client.get(url_for("portfolios.portfolios"))

    assert response.status_code == 200
    assert portfolio.name.encode("utf8") in response.data
    assert (
        translate("portfolios.index.empty.start_button").encode("utf8")
        not in response.data
    )


def test_portfolio_index_without_existing_portfolios(client, user_session):
    user = UserFactory.create()
    user_session(user)

    response = client.get(url_for("portfolios.portfolios"))

    assert response.status_code == 200
    assert (
        translate("portfolios.index.empty.start_button").encode("utf8") in response.data
    )
