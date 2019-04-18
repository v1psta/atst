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
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
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
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
        not in response.data.decode()
    )


def test_user_with_permission_has_add_application_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.create_application", portfolio_id=portfolio.id)
        in response.data.decode()
    )


def test_user_without_permission_has_no_add_application_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio)
    user_session(user)
    response = client.get(
        url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
    )
    assert (
        url_for("portfolios.create_application", portfolio_id=portfolio.id)
        not in response.data.decode()
    )


def test_creating_application(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.create_application", portfolio_id=portfolio.id),
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


def test_view_edit_application(client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    user_session(portfolio.owner)
    response = client.get(
        url_for(
            "portfolios.update_application",
            portfolio_id=portfolio.id,
            application_id=application.id,
        )
    )
    assert response.status_code == 200


def test_edit_application_environments_obj(app, client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    env1 = application.environments[0]
    env2 = application.environments[1]
    env_role1 = EnvironmentRoleFactory.create(environment=env1, user=user1)
    env_role2 = EnvironmentRoleFactory.create(environment=env1, user=user2)
    env_role3 = EnvironmentRoleFactory.create(environment=env2, user=user1)

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for(
                "portfolios.edit_application",
                portfolio_id=portfolio.id,
                application_id=application.id,
            )
        )

        assert response.status_code == 200
        _, context = templates[0]
        assert context["environments_obj"] == {
            env1.name: [
                {"name": user1.full_name, "role": env_role1.role},
                {"name": user2.full_name, "role": env_role2.role},
            ],
            env2.name: [{"name": user1.full_name, "role": env_role3.role}],
        }


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


def test_user_can_only_access_apps_in_their_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create(
        applications=[
            {
                "name": "Awesome Application",
                "description": "More cool stuff happening here!",
                "environments": [{"name": "dev"}],
            }
        ]
    )
    other_application = other_portfolio.applications[0]
    user_session(portfolio.owner)

    # user can't view application edit form
    response = client.get(
        url_for(
            "portfolios.edit_application",
            portfolio_id=portfolio.id,
            application_id=other_application.id,
        )
    )
    assert response.status_code == 404

    # user can't post update application form
    time_updated = other_application.time_updated
    response = client.post(
        url_for(
            "portfolios.update_application",
            portfolio_id=portfolio.id,
            application_id=other_application.id,
        ),
        data={"name": "New Name", "description": "A new description."},
    )
    assert response.status_code == 404
    assert time_updated == other_application.time_updated


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


def test_delete_application(client, user_session):
    user = UserFactory.create()
    port = PortfolioFactory.create(
        owner=user,
        applications=[
            {
                "name": "mos eisley",
                "environments": [
                    {"name": "bar"},
                    {"name": "booth"},
                    {"name": "band stage"},
                ],
            }
        ],
    )
    application = port.applications[0]
    user_session(user)

    response = client.post(
        url_for(
            "portfolios.delete_application",
            portfolio_id=port.id,
            application_id=application.id,
        )
    )
    # appropriate response and redirect
    assert response.status_code == 302
    assert response.location == url_for(
        "portfolios.portfolio_applications", portfolio_id=port.id, _external=True
    )
    # appropriate flash message
    message = get_flashed_messages()[0]
    assert "deleted" in message["message"]
    assert application.name in message["message"]
    # app and envs are soft deleted
    assert len(port.applications) == 0
    assert len(application.environments) == 0


def test_edit_application_scope(client, user_session):
    owner = UserFactory.create()
    port1 = PortfolioFactory.create(owner=owner, applications=[{"name": "first app"}])
    port2 = PortfolioFactory.create(owner=owner, applications=[{"name": "second app"}])

    user_session(owner)
    response = client.get(
        url_for(
            "portfolios.edit_application",
            portfolio_id=port2.id,
            application_id=port1.applications[0].id,
        )
    )

    assert response.status_code == 404


def test_application_team(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)

    user_session(portfolio.owner)

    response = client.get(
        url_for(
            "portfolios.application_team",
            portfolio_id=portfolio.id,
            application_id=application.id,
        )
    )

    assert response.status_code == 200
