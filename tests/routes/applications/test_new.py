from flask import url_for

from tests.factories import PortfolioFactory


def test_creating_application(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for("applications.create", portfolio_id=portfolio.id),
        data={
            "name": "Test Application",
            "description": "This is only a test",
            "environment_names-0": "dev",
            "environment_names-1": "staging",
            "environment_names-2": "prod",
        },
    )
    assert response.status_code == 302
    assert len(portfolio.applications) == 1
    assert len(portfolio.applications[0].environments) == 3
