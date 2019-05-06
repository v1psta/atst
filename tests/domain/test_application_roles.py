from atst.domain.application_roles import ApplicationRoles
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
