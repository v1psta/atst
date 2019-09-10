import pytest
import uuid
from flask import url_for, get_flashed_messages
from unittest.mock import Mock

from tests.factories import *

from atst.domain.applications import Applications
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.common import Paginator
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolios import Portfolios
from atst.domain.exceptions import NotFoundError
from atst.models.environment_role import CSPRole
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from atst.forms.application import EditEnvironmentForm
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
    app_role1 = ApplicationRoleFactory.create(application=application)
    env_role1 = EnvironmentRoleFactory.create(
        application_role=app_role1, environment=env, role=CSPRole.BASIC_ACCESS.value
    )
    app_role2 = ApplicationRoleFactory.create(application=application, user=None)
    invite = ApplicationInvitationFactory.create(role=app_role2)
    env_role2 = EnvironmentRoleFactory.create(
        application_role=app_role2, environment=env, role=CSPRole.NETWORK_ADMIN.value
    )

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[-1]

        env_obj = context["environments_obj"][0]
        assert env_obj["name"] == env.name
        assert env_obj["id"] == env.id
        assert isinstance(env_obj["edit_form"], EditEnvironmentForm)
        assert (
            env_obj["members"].sort()
            == [app_role1.user_name, app_role2.user_name].sort()
        )
        assert isinstance(context["audit_events"], Paginator)


def test_data_for_app_env_roles_form(app, client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env"},
    )
    env = application.environments[0]
    app_role0 = ApplicationRoleFactory.create(application=application)
    app_role1 = ApplicationRoleFactory.create(application=application)
    env_role1 = EnvironmentRoleFactory.create(
        application_role=app_role1, environment=env, role=CSPRole.BASIC_ACCESS.value
    )
    app_role2 = ApplicationRoleFactory.create(application=application)
    env_role2 = EnvironmentRoleFactory.create(
        application_role=app_role2, environment=env, role=CSPRole.NETWORK_ADMIN.value
    )

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[-1]


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


def test_create_member(monkeypatch, client, user_session, session):
    job_mock = Mock()
    monkeypatch.setattr("atst.jobs.send_mail.delay", job_mock)
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    env = application.environments[0]
    env_1 = application.environments[1]

    user_session(application.portfolio.owner)

    response = client.post(
        url_for("applications.create_member", application_id=application.id),
        data={
            "user_data-first_name": user.first_name,
            "user_data-last_name": user.last_name,
            "user_data-dod_id": user.dod_id,
            "user_data-email": user.email,
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "Basic Access",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-role": NO_ACCESS,
            "environment_roles-1-environment_name": env_1.name,
            "permission_sets-perms_env_mgmt": True,
            "permission_sets-perms_team_mgmt": True,
            "permission_sets-perms_del_env": True,
        },
    )

    assert response.status_code == 302
    expected_url = url_for(
        "applications.settings",
        application_id=application.id,
        fragment="application-members",
        _anchor="application-members",
        _external=True,
    )
    assert response.location == expected_url
    assert len(application.roles) == 1
    environment_roles = application.roles[0].environment_roles
    assert len(environment_roles) == 1
    assert environment_roles[0].environment == env

    invitation = (
        session.query(ApplicationInvitation).filter_by(dod_id=user.dod_id).one()
    )
    assert invitation.role.application == application

    assert job_mock.called


def test_remove_member_success(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create()
    application_role = ApplicationRoleFactory.create(application=application, user=user)

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=application_role.id,
        )
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        _anchor="application-members",
        _external=True,
        application_id=application.id,
        fragment="application-members",
    )


def test_remove_new_member_success(client, user_session):
    application = ApplicationFactory.create()
    application_role = ApplicationRoleFactory.create(application=application, user=None)

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=application_role.id,
        )
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        _anchor="application-members",
        _external=True,
        application_id=application.id,
        fragment="application-members",
    )


def test_remove_member_failure(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create()

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=uuid.uuid4(),
        )
    )

    assert response.status_code == 404
