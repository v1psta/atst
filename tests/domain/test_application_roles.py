import pytest

from atst.domain.application_roles import ApplicationRoles
from atst.domain.exceptions import NotFoundError
from atst.domain.permission_sets import PermissionSets
from atst.models import ApplicationRoleStatus

from tests.factories import *


def test_create_application_role():
    application = ApplicationFactory.create()
    user = UserFactory.create()

    application_role = ApplicationRoles.create(
        application=application,
        user=user,
        permission_set_names=[PermissionSets.EDIT_APPLICATION_TEAM],
    )

    assert application_role.permission_sets == PermissionSets.get_many(
        [PermissionSets.EDIT_APPLICATION_TEAM, PermissionSets.VIEW_APPLICATION]
    )
    assert application_role.application == application
    assert application_role.user == user


def test_enabled_application_role():
    application = ApplicationFactory.create()
    user = UserFactory.create()
    app_role = ApplicationRoleFactory.create(
        application=application, user=user, status=ApplicationRoleStatus.DISABLED
    )
    assert app_role.status == ApplicationRoleStatus.DISABLED

    ApplicationRoles.enable(app_role, app_role.user)

    assert app_role.status == ApplicationRoleStatus.ACTIVE


def test_get():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=user, application=application)

    assert ApplicationRoles.get(user.id, application.id)
    assert app_role.application == application
    assert app_role.user == user


def test_get_handles_invalid_id():
    user = UserFactory.create()
    application = ApplicationFactory.create()

    with pytest.raises(NotFoundError):
        ApplicationRoles.get(user.id, application.id)


def test_get_by_id():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=user, application=application)

    assert ApplicationRoles.get_by_id(app_role.id) == app_role
    app_role.status = ApplicationRoleStatus.DISABLED

    with pytest.raises(NotFoundError):
        ApplicationRoles.get_by_id(app_role.id)


def test_disable():
    application = ApplicationFactory.create()
    user = UserFactory.create()
    member_role = ApplicationRoleFactory.create(application=application, user=user)
    environment = EnvironmentFactory.create(application=application)
    environment_role = EnvironmentRoleFactory.create(
        application_role=member_role, environment=environment
    )
    assert member_role == ApplicationRoles.get(
        user_id=user.id, application_id=application.id
    )
    ApplicationRoles.disable(member_role)
    assert (
        ApplicationRoles.get(user_id=user.id, application_id=application.id).status
        == ApplicationRoleStatus.DISABLED
    )
