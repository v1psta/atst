from flask import url_for

from tests.factories import PortfolioFactory, ApplicationFactory


def test_application_team(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)

    user_session(portfolio.owner)

    response = client.get(url_for("applications.team", application_id=application.id))

    assert response.status_code == 200
