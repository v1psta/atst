import pytest

from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import NotFoundError
from atst.models.environment_role import CSPRole

from tests.factories import (
    ApplicationFactory,
    UserFactory,
    PortfolioFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    ApplicationRoleFactory,
)


def test_create_environments():
    application = ApplicationFactory.create()
    environments = Environments.create_many(application, ["Staging", "Production"])
    for env in environments:
        assert env.cloud_id is not None


def test_update_env_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.TECHNICAL_READ.value
    ApplicationRoleFactory.create(
        user=env_role.user, application=env_role.environment.application
    )

    assert Environments.update_env_role(env_role.environment, env_role.user, new_role)
    assert env_role.role == new_role


def test_update_env_role_no_access():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    ApplicationRoleFactory.create(
        user=env_role.user, application=env_role.environment.application
    )

    assert Environments.update_env_role(
        env_role.environment, env_role.user, "no_access"
    )
    assert not EnvironmentRoles.get(env_role.user.id, env_role.environment.id)


def test_update_env_role_no_change():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.BASIC_ACCESS.value

    assert not Environments.update_env_role(
        env_role.environment, env_role.user, new_role
    )


def test_update_env_role_creates_cloud_id_for_new_member(session):
    user = UserFactory.create()
    env = EnvironmentFactory.create()
    ApplicationRoleFactory.create(user=user, application=env.application)
    assert not user.cloud_id
    assert Environments.update_env_role(env, user, CSPRole.TECHNICAL_READ.value)
    assert EnvironmentRoles.get(user.id, env.id)
    assert user.cloud_id is not None


def test_update_env_roles_by_environment():
    environment = EnvironmentFactory.create()
    env_role_1 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.BASIC_ACCESS.value
    )
    env_role_2 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.NETWORK_ADMIN.value
    )
    env_role_3 = EnvironmentRoleFactory.create(
        environment=environment, role=CSPRole.TECHNICAL_READ.value
    )
    for user in [env_role_1.user, env_role_2.user, env_role_3.user]:
        ApplicationRoleFactory.create(user=user, application=environment.application)

    team_roles = [
        {
            "user_id": env_role_1.user.id,
            "name": env_role_1.user.full_name,
            "role": CSPRole.BUSINESS_READ.value,
        },
        {
            "user_id": env_role_2.user.id,
            "name": env_role_2.user.full_name,
            "role": CSPRole.NETWORK_ADMIN.value,
        },
        {
            "user_id": env_role_3.user.id,
            "name": env_role_3.user.full_name,
            "role": "no_access",
        },
    ]

    Environments.update_env_roles_by_environment(environment.id, team_roles)
    assert env_role_1.role == CSPRole.BUSINESS_READ.value
    assert env_role_2.role == CSPRole.NETWORK_ADMIN.value
    assert not EnvironmentRoles.get(env_role_3.user.id, environment.id)


def test_update_env_roles_by_member():
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[
            {
                "name": "dev",
                "members": [{"user": user, "role_name": CSPRole.BUSINESS_READ.value}],
            },
            {
                "name": "staging",
                "members": [{"user": user, "role_name": CSPRole.BUSINESS_READ.value}],
            },
            {"name": "prod"},
            {
                "name": "testing",
                "members": [{"user": user, "role_name": CSPRole.BUSINESS_READ.value}],
            },
        ]
    )

    dev, staging, prod, testing = application.environments
    env_roles = [
        {"id": dev.id, "role": CSPRole.NETWORK_ADMIN.value},
        {"id": staging.id, "role": CSPRole.BUSINESS_READ.value},
        {"id": prod.id, "role": CSPRole.TECHNICAL_READ.value},
        {"id": testing.id, "role": "no_access"},
    ]

    Environments.update_env_roles_by_member(user, env_roles)

    assert EnvironmentRoles.get(user.id, dev.id).role == CSPRole.NETWORK_ADMIN.value
    assert EnvironmentRoles.get(user.id, staging.id).role == CSPRole.BUSINESS_READ.value
    assert EnvironmentRoles.get(user.id, prod.id).role == CSPRole.TECHNICAL_READ.value
    assert not EnvironmentRoles.get(user.id, testing.id)


def test_get_scoped_environments(db):
    developer = UserFactory.create()
    portfolio = PortfolioFactory.create(
        members=[{"user": developer, "role_name": "developer"}],
        applications=[
            {
                "name": "application1",
                "environments": [
                    {
                        "name": "application1 dev",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "application1 staging"},
                    {"name": "application1 prod"},
                ],
            },
            {
                "name": "application2",
                "environments": [
                    {"name": "application2 dev"},
                    {
                        "name": "application2 staging",
                        "members": [{"user": developer, "role_name": "developer"}],
                    },
                    {"name": "application2 prod"},
                ],
            },
        ],
    )

    application1_envs = Environments.for_user(developer, portfolio.applications[0])
    assert [env.name for env in application1_envs] == ["application1 dev"]

    application2_envs = Environments.for_user(developer, portfolio.applications[1])
    assert [env.name for env in application2_envs] == ["application2 staging"]


def test_get_excludes_deleted():
    env = EnvironmentFactory.create(
        deleted=True, application=ApplicationFactory.create()
    )
    with pytest.raises(NotFoundError):
        Environments.get(env.id)


def test_delete_environment(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env_role = EnvironmentRoleFactory.create(user=UserFactory.create(), environment=env)
    assert not env.deleted
    assert not env_role.deleted
    Environments.delete(env)
    assert env.deleted
    assert env_role.deleted
    # did not flush
    assert session.dirty

    Environments.delete(env, commit=True)
    assert env.deleted
    assert env_role.deleted
    # flushed the change
    assert not session.dirty


def test_update_environment():
    environment = EnvironmentFactory.create()
    assert environment.name is not "name 2"
    Environments.update(environment, name="name 2")
    assert environment.name == "name 2"
