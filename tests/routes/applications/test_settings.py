import pytest
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
from atst.routes.applications.settings import check_users_are_in_application

from atst.domain.applications import Applications
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolios import Portfolios
from atst.domain.exceptions import NotFoundError
from atst.models.environment_role import CSPRole
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from atst.forms.application import EditEnvironmentForm
from atst.forms.app_settings import AppEnvRolesForm
from atst.forms.data import ENV_ROLE_NO_ACCESS as NO_ACCESS

from tests.utils import captured_templates


def test_updating_application_environments_success(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    user_session(portfolio.owner)

    form_data = {"name": "new name a"}

    response = client.post(
        url_for("applications.update_environment", environment_id=environment.id),
        data=form_data,
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        application_id=application.id,
        _external=True,
        fragment="application-environments",
        _anchor="application-environments",
        active_toggler=environment.id,
        active_toggler_section="edit",
    )
    assert environment.name == "new name a"


def test_update_environment_failure(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(
        application=application, name="original name"
    )

    user_session(portfolio.owner)

    form_data = {"name": ""}

    response = client.post(
        url_for("applications.update_environment", environment_id=environment.id),
        data=form_data,
    )

    assert response.status_code == 400
    assert environment.name == "original name"


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
        {"env"},
    )
    env = application.environments[0]
    app_role = ApplicationRoleFactory.create(application=application)
    env_role1 = EnvironmentRoleFactory.create(
        environment=env, role=CSPRole.BASIC_ACCESS.value
    )
    ApplicationRoleFactory.create(application=application, user=env_role1.user)
    env_role2 = EnvironmentRoleFactory.create(
        environment=env, role=CSPRole.NETWORK_ADMIN.value
    )
    ApplicationRoleFactory.create(application=application, user=env_role2.user)

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[0]

        assert isinstance(context["members_form"], AppEnvRolesForm)
        env_obj = context["environments_obj"][0]
        assert env_obj["name"] == env.name
        assert env_obj["id"] == env.id
        assert isinstance(env_obj["edit_form"], EditEnvironmentForm)
        assert (
            env_obj["members"].sort()
            == [env_role1.user.full_name, env_role2.user.full_name].sort()
        )


def test_data_for_app_env_roles_form(app, client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env"},
    )
    env = application.environments[0]
    app_role = ApplicationRoleFactory.create(application=application)
    env_role1 = EnvironmentRoleFactory.create(
        environment=env, role=CSPRole.BASIC_ACCESS.value
    )
    ApplicationRoleFactory.create(application=application, user=env_role1.user)
    env_role2 = EnvironmentRoleFactory.create(
        environment=env, role=CSPRole.NETWORK_ADMIN.value
    )
    ApplicationRoleFactory.create(application=application, user=env_role2.user)

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[0]

        members_form = context["members_form"]
        assert isinstance(members_form, AppEnvRolesForm)
        assert members_form.data == {
            "envs": [
                {
                    "env_id": env.id,
                    "team_roles": [
                        {
                            "role": NO_ACCESS,
                            "members": [
                                {
                                    "user_id": str(app_role.user_id),
                                    "user_name": app_role.user.full_name,
                                    "role_name": None,
                                }
                            ],
                        },
                        {
                            "role": CSPRole.BASIC_ACCESS.value,
                            "members": [
                                {
                                    "user_id": str(env_role1.user_id),
                                    "user_name": env_role1.user.full_name,
                                    "role_name": CSPRole.BASIC_ACCESS.value,
                                }
                            ],
                        },
                        {
                            "role": CSPRole.NETWORK_ADMIN.value,
                            "members": [
                                {
                                    "user_id": str(env_role2.user_id),
                                    "user_name": env_role2.user.full_name,
                                    "role_name": CSPRole.NETWORK_ADMIN.value,
                                }
                            ],
                        },
                        {"role": CSPRole.BUSINESS_READ.value, "members": []},
                        {"role": CSPRole.TECHNICAL_READ.value, "members": []},
                    ],
                }
            ]
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


def test_check_users_are_in_application_raises_NotFoundError():
    application = ApplicationFactory.create()
    app_user_1 = UserFactory.create()
    app_user_2 = UserFactory.create()
    for user in [app_user_1, app_user_2]:
        ApplicationRoleFactory.create(user=user, application=application)

    non_app_user = UserFactory.create()
    user_ids = [app_user_1.id, app_user_2.id, non_app_user.id]
    with pytest.raises(NotFoundError):
        check_users_are_in_application(user_ids, application)


def test_check_users_are_in_application():
    application = ApplicationFactory.create()
    app_user_1 = UserFactory.create()
    app_user_2 = UserFactory.create()
    app_user_3 = UserFactory.create()

    for user in [app_user_1, app_user_2, app_user_3]:
        ApplicationRoleFactory.create(user=user, application=application)

    user_ids = [str(app_user_1.id), str(app_user_2.id), str(app_user_3.id)]
    assert check_users_are_in_application(user_ids, application)


def test_update_team_env_roles(client, user_session):
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
    for user in [env_role_1.user, env_role_2.user, env_role_3.user]:
        ApplicationRoleFactory.create(user=user, application=application)

    app_role = ApplicationRoleFactory.create(application=application)
    form_data = {
        "envs-0-env_id": environment.id,
        "envs-0-team_roles-0-members-0-user_id": app_role.user.id,
        "envs-0-team_roles-0-members-0-role_name": CSPRole.TECHNICAL_READ.value,
        "envs-0-team_roles-1-members-0-user_id": env_role_1.user.id,
        "envs-0-team_roles-1-members-0-role_name": CSPRole.NETWORK_ADMIN.value,
        "envs-0-team_roles-1-members-1-user_id": env_role_2.user.id,
        "envs-0-team_roles-1-members-1-role_name": CSPRole.BASIC_ACCESS.value,
        "envs-0-team_roles-1-members-2-user_id": env_role_3.user.id,
        "envs-0-team_roles-1-members-2-role_name": NO_ACCESS,
    }

    user_session(application.portfolio.owner)
    response = client.post(
        url_for("applications.update_env_roles", environment_id=environment.id),
        data=form_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert env_role_1.role == CSPRole.NETWORK_ADMIN.value
    assert env_role_2.role == CSPRole.BASIC_ACCESS.value
    assert not EnvironmentRoles.get(env_role_3.user.id, environment.id)
    assert EnvironmentRoles.get(app_role.user.id, environment.id)


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


def test_new_environment(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    num_envs = len(application.environments)

    user_session(user)
    response = client.post(
        url_for("applications.new_environment", application_id=application.id),
        data={"name": "dabea"},
    )

    assert response.status_code == 302
    assert len(application.environments) == num_envs + 1


def test_new_environment_with_bad_data(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    num_envs = len(application.environments)

    user_session(user)
    response = client.post(
        url_for("applications.new_environment", application_id=application.id),
        data={"name": None},
    )

    assert response.status_code == 400
    assert len(application.environments) == num_envs


def test_delete_environment(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    user_session(user)

    response = client.post(
        url_for("applications.delete_environment", environment_id=environment.id)
    )

    # appropriate response and redirect
    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        application_id=application.id,
        _anchor="application-environments",
        _external=True,
        fragment="application-environments",
    )
    # appropriate flash message
    message = get_flashed_messages()[0]
    assert "deleted" in message["message"]
    assert environment.name in message["message"]
    # deletes environment
    assert len(application.environments) == 0
