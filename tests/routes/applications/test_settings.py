from flask import url_for, get_flashed_messages

from tests.factories import (
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    EnvironmentRoleFactory,
    EnvironmentFactory,
    ApplicationFactory,
    ApplicationRoleFactory,
)

from atst.domain.applications import Applications
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolios import Portfolios
from atst.models.environment_role import CSPRole
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.utils import captured_templates


def test_application_settings(client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.settings", application_id=application.id)
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
            url_for("applications.settings", application_id=application.id)
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


def test_edit_app_serialize_env_member_form_data(app, client, user_session):
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
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[0]
        for env_id in context["env_forms"]:
            env = Environments.get(environment_id=env_id)
            form_data = {"env_id": env_id, "team_roles": []}
            for user in env.users:
                env_role = EnvironmentRoles.get(user.id, env.id)
                form_data["team_roles"].append(
                    {
                        "name": user.full_name,
                        "user_id": user.id,
                        "role": env_role.displayname,
                    }
                )

            assert context["env_forms"][env_id].data == form_data


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
        url_for("applications.update", application_id=application.id),
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
        url_for("applications.update", application_id=application.id),
        data={"name": "New Name", "description": "A new description."},
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert application.name == "Great Application"
    assert application.description == "Cool stuff happening here!"


def test_user_with_permission_can_update_team_env_roles(client, user_session):
    environment = EnvironmentFactory.create()
    application = environment.application
    env_role_1 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    env_role_2 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    env_role_3 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    app_role = ApplicationRoleFactory.create(application=application)
    form_data = {
        "env_id": environment.id,
        "team_roles-0-user_id": env_role_1.user.id,
        "team_roles-0-name": env_role_1.user.full_name,
        "team_roles-0-role": CSPRole.NETWORK_ADMIN.value,
        "team_roles-1-user_id": env_role_2.user.id,
        "team_roles-1-name": env_role_2.user.full_name,
        "team_roles-1-role": CSPRole.BASIC_ACCESS.value,
        "team_roles-2-user_id": env_role_3.user.id,
        "team_roles-2-name": env_role_3.user.full_name,
        "team_roles-2-role": "",
        "team_roles-3-user_id": app_role.user.id,
        "team_roles-3-name": app_role.user.full_name,
        "team_roles-3-role": CSPRole.TECHNICAL_READ.value,
    }

    user_session(application.portfolio.owner)
    response = client.post(
        url_for("applications.update_env_roles", application_id=application.id),
        data=form_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert env_role_1.role == CSPRole.NETWORK_ADMIN.value
    assert env_role_2.role == CSPRole.BASIC_ACCESS.value
    assert not EnvironmentRoles.get(env_role_3.user.id, environment.id)
    assert EnvironmentRoles.get(app_role.user.id, environment.id)


def test_user_without_permission_cannot_update_team_env_roles(client, user_session):
    environment = EnvironmentFactory.create()
    application = environment.application
    app_role_without_perms = ApplicationRoleFactory.create(application=application)
    env_role_1 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    env_role_2 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    app_role = ApplicationRoleFactory.create(application=application)
    form_data = {
        "env_id": environment.id,
        "team_roles-0-user_id": env_role_1.user.id,
        "team_roles-0-name": env_role_1.user.full_name,
        "team_roles-0-role": CSPRole.NETWORK_ADMIN.value,
        "team_roles-1-user_id": env_role_2.user.id,
        "team_roles-1-name": env_role_2.user.full_name,
        "team_roles-1-role": "",
        "team_roles-2-user_id": app_role.user.id,
        "team_roles-2-name": app_role.user.full_name,
        "team_roles-2-role": CSPRole.TECHNICAL_READ.value,
    }

    user_session(app_role_without_perms.user)
    response = client.post(
        url_for("applications.update_env_roles", application_id=application.id),
        data=form_data,
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert env_role_1.role == CSPRole.BASIC_ACCESS.value
    assert (
        EnvironmentRoles.get(env_role_2.user.id, environment.id).role
        == CSPRole.BASIC_ACCESS.value
    )
    assert not EnvironmentRoles.get(app_role.user.id, environment.id)


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
        url_for("applications.settings", application_id=other_application.id)
    )
    assert response.status_code == 404

    # user can't post update application form
    time_updated = other_application.time_updated
    response = client.post(
        url_for("applications.update", application_id=other_application.id),
        data={"name": "New Name", "description": "A new description."},
    )
    assert response.status_code == 404
    assert time_updated == other_application.time_updated


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
        url_for("applications.delete", application_id=application.id)
    )
    # appropriate response and redirect
    assert response.status_code == 302
    assert response.location == url_for(
        "applications.portfolio_applications", portfolio_id=port.id, _external=True
    )
    # appropriate flash message
    message = get_flashed_messages()[0]
    assert "deleted" in message["message"]
    assert application.name in message["message"]
    # app and envs are soft deleted
    assert len(port.applications) == 0
    assert len(application.environments) == 0
