from flask import url_for

from tests.factories import PortfolioFactory


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
