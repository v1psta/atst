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


@pytest.mark.skip(reason="Reinstate and update once jobs api is up")
def test_create_environments():
    application = ApplicationFactory.create()
    environments = Environments.create_many(application, ["Staging", "Production"])
    for env in environments:
        assert env.cloud_id is not None


def test_update_env_role():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.TECHNICAL_READ.value

    assert Environments.update_env_role(
        env_role.environment, env_role.application_role, new_role
    )
    assert env_role.role == new_role


def test_update_env_role_no_access():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)

    assert Environments.update_env_role(
        env_role.environment, env_role.application_role, None
    )
    assert not EnvironmentRoles.get(
        env_role.application_role.id, env_role.environment.id
    )


def test_update_env_role_no_change():
    env_role = EnvironmentRoleFactory.create(role=CSPRole.BASIC_ACCESS.value)
    new_role = CSPRole.BASIC_ACCESS.value

    assert not Environments.update_env_role(
        env_role.environment, env_role.application_role, new_role
    )


def test_get_excludes_deleted():
    env = EnvironmentFactory.create(
        deleted=True, application=ApplicationFactory.create()
    )
    with pytest.raises(NotFoundError):
        Environments.get(env.id)


def test_delete_environment(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env_role = EnvironmentRoleFactory.create(
        application_role=ApplicationRoleFactory.create(application=env.application),
        environment=env,
    )
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
