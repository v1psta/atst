from atst.domain.environment_roles import EnvironmentRoles

from tests.factories import *


def test_get_for_application_and_user():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    env1 = EnvironmentFactory.create(application=application)
    EnvironmentFactory.create(application=application)
    EnvironmentRoleFactory.create(user=user, environment=env1)

    roles = EnvironmentRoles.get_for_application_and_user(user.id, application.id)
    assert len(roles) == 1
    assert roles[0].environment == env1
    assert roles[0].user == user


def test_get_for_application_and_user_does_not_return_deleted():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    env1 = EnvironmentFactory.create(application=application)
    EnvironmentRoleFactory.create(user=user, environment=env1, deleted=True)

    roles = EnvironmentRoles.get_for_application_and_user(user.id, application.id)
    assert len(roles) == 0
