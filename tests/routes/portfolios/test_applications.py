from flask import url_for

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
from atst.domain.roles import Roles
from atst.models.portfolio_role import Status as PortfolioRoleStatus


def test_user_with_permission_has_budget_report_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/reports"'.format(portfolio.id).encode() in response.data
    )


def test_user_without_permission_has_no_budget_report_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(
        user, portfolio, "developer", status=PortfolioRoleStatus.ACTIVE
    )
    user_session(user)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/reports"'.format(portfolio.id).encode()
        not in response.data
    )


def test_user_with_permission_has_activity_log_link(client, user_session):
    portfolio = PortfolioFactory.create()
    ccpo = UserFactory.from_atat_role("ccpo")
    admin = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=admin,
        role=Roles.get("admin"),
        status=PortfolioRoleStatus.ACTIVE,
    )

    user_session(portfolio.owner)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/activity"'.format(portfolio.id).encode() in response.data
    )

    # logs out previous user before creating a new session
    user_session(admin)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/activity"'.format(portfolio.id).encode() in response.data
    )

    user_session(ccpo)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/activity"'.format(portfolio.id).encode() in response.data
    )


def test_user_without_permission_has_no_activity_log_link(client, user_session):
    portfolio = PortfolioFactory.create()
    developer = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=developer,
        role=Roles.get("developer"),
        status=PortfolioRoleStatus.ACTIVE,
    )

    user_session(developer)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/activity"'.format(portfolio.id).encode()
        not in response.data
    )


def test_user_with_permission_has_add_application_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/applications/new"'.format(portfolio.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_application_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio, "developer")
    user_session(user)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert (
        'href="/portfolios/{}/applications/new"'.format(portfolio.id).encode()
        not in response.data
    )


def test_view_edit_application(client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    user_session(portfolio.owner)
    response = client.get(
        "/portfolios/{}/applications/{}/edit".format(portfolio.id, application.id)
    )
    assert response.status_code == 200


def test_user_with_permission_can_update_application(client, user_session):
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[
            {
                "name": "Awesome Application",
                "description": "It's really awesome!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    application = portfolio.applications[0]
    user_session(owner)
    response = client.post(
        url_for(
            "portfolios.update_application",
            portfolio_id=portfolio.id,
            application_id=application.id,
        ),
        data={
            "name": "Really Cool Application",
            "description": "A very cool application.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert application.name == "Really Cool Application"
    assert application.description == "A very cool application."


def test_user_without_permission_cannot_update_application(client, user_session):
    dev = UserFactory.create()
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": dev, "role_name": "developer"}],
        applications=[
            {
                "name": "Great Application",
                "description": "Cool stuff happening here!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    application = portfolio.applications[0]
    user_session(dev)
    response = client.post(
        url_for(
            "portfolios.update_application",
            portfolio_id=portfolio.id,
            application_id=application.id,
        ),
        data={"name": "New Name", "description": "A new description."},
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert application.name == "Great Application"
    assert application.description == "Cool stuff happening here!"


def create_environment(user):
    portfolio = PortfolioFactory.create()
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    return EnvironmentFactory.create(application=application, name="new environment!")


def test_environment_access_with_env_role(client, user_session):
    user = UserFactory.create()
    environment = create_environment(user)
    env_role = EnvironmentRoleFactory.create(
        user=user, environment=environment, role="developer"
    )
    user_session(user)
    response = client.get(
        url_for(
            "portfolios.access_environment",
            portfolio_id=environment.portfolio.id,
            environment_id=environment.id,
        )
    )
    assert response.status_code == 302
    assert "csp-environment-access" in response.location


def test_environment_access_with_no_role(client, user_session):
    user = UserFactory.create()
    environment = create_environment(user)
    user_session(user)
    response = client.get(
        url_for(
            "portfolios.access_environment",
            portfolio_id=environment.portfolio.id,
            environment_id=environment.id,
        )
    )
    assert response.status_code == 404
