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

    ApplicationRoles.enable(app_role)

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


def test_update_permission_sets():
    user = UserFactory.create()
    application = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=user, application=application)

    view_app = [PermissionSets.get(PermissionSets.VIEW_APPLICATION)]
    new_perms_names = [
        PermissionSets.EDIT_APPLICATION_TEAM,
        PermissionSets.DELETE_APPLICATION_ENVIRONMENTS,
    ]
    new_perms = PermissionSets.get_many(new_perms_names)
    # view application permission is included by default
    assert app_role.permission_sets == view_app
    assert ApplicationRoles.update_permission_sets(app_role, new_perms_names)
    assert set(app_role.permission_sets) == set(new_perms + view_app)
