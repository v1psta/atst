from flask import url_for

from tests.factories import PortfolioFactory, ApplicationFactory
from atst.domain.applications import Applications


def test_get_name_and_description_form(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.view_new_application_step_1", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200


def test_get_name_and_description_form_for_update(client, user_session):
    name = "My Test Application"
    description = "This is the description of the test application."
    application = ApplicationFactory.create(name=name, description=description)
    user_session(application.portfolio.owner)
    response = client.get(
        url_for(
            "applications.view_new_application_step_1",
            portfolio_id=application.portfolio.id,
            application_id=application.id,
        )
    )
    assert response.status_code == 200
    assert name in response.data.decode()
    assert description in response.data.decode()


def test_post_name_and_description(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "applications.create_new_application_step_1", portfolio_id=portfolio.id
        ),
        data={"name": "Test Application", "description": "This is only a test"},
    )
    assert response.status_code == 302
    assert len(portfolio.applications) == 1
    assert portfolio.applications[0].name == "Test Application"
    assert portfolio.applications[0].description == "This is only a test"


def test_post_name_and_description_for_update(client, session, user_session):
    application = ApplicationFactory.create()
    user_session(application.portfolio.owner)
    response = client.post(
        url_for(
            "applications.update_new_application_step_1",
            portfolio_id=application.portfolio.id,
            application_id=application.id,
        ),
        data={"name": "Test Application", "description": "This is only a test"},
    )
    assert response.status_code == 302

    session.refresh(application)
    assert application.name == "Test Application"
    assert application.description == "This is only a test"


def test_get_environments(client, user_session):
    application = ApplicationFactory.create()
    user_session(application.portfolio.owner)
    response = client.get(
        url_for(
            "applications.view_new_application_step_2",
            portfolio_id=application.portfolio.id,
            application_id=application.id,
        )
    )
    assert response.status_code == 200


def test_post_environments(client, session, user_session):
    application = ApplicationFactory.create(environments=[])
    user_session(application.portfolio.owner)
    response = client.post(
        url_for(
            "applications.update_new_application_step_2",
            portfolio_id=application.portfolio.id,
            application_id=application.id,
        ),
        data={
            "environment_names-0": "development",
            "environment_names-1": "staging",
            "environment_names-2": "production",
        },
    )
    assert response.status_code == 302
    session.refresh(application)
    assert len(application.environments) == 3
