from atst.domain.application_roles import ApplicationRoles
from atst.domain.permission_sets import PermissionSets
from tests.factories import UserFactory, ApplicationFactory


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
