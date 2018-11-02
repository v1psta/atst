from atst.domain.workspace_roles import WorkspaceRoles
from atst.domain.users import Users
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from atst.domain.roles import Roles

from tests.factories import (
    WorkspaceFactory,
    UserFactory,
    InvitationFactory,
    WorkspaceRoleFactory,
)


def test_can_create_new_workspace_role():
    workspace = WorkspaceFactory.create()
    new_user = UserFactory.create()

    workspace_role_dicts = [{"id": new_user.id, "workspace_role": "owner"}]
    workspace_roles = WorkspaceRoles.add_many(workspace.id, workspace_role_dicts)

    assert workspace_roles[0].user_id == new_user.id
    assert workspace_roles[0].user.atat_role.name == new_user.atat_role.name
    assert workspace_roles[0].role.name == new_user.workspace_roles[0].role.name


def test_can_update_existing_workspace_role():
    workspace = WorkspaceFactory.create()
    new_user = UserFactory.create()

    WorkspaceRoles.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "owner"}]
    )
    workspace_roles = WorkspaceRoles.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "developer"}]
    )

    assert workspace_roles[0].user.atat_role.name == new_user.atat_role.name
    assert workspace_roles[0].role.name == new_user.workspace_roles[0].role.name


def test_workspace_role_permissions():
    workspace_one = WorkspaceFactory.create()
    workspace_two = WorkspaceFactory.create()
    new_user = UserFactory.create()
    WorkspaceRoleFactory.create(
        workspace=workspace_one,
        user=new_user,
        role=Roles.get("developer"),
        status=WorkspaceRoleStatus.ACTIVE,
    )
    WorkspaceRoleFactory.create(
        workspace=workspace_two,
        user=new_user,
        role=Roles.get("developer"),
        status=WorkspaceRoleStatus.PENDING,
    )

    assert WorkspaceRoles.workspace_role_permissions(workspace_one, new_user)
    assert not WorkspaceRoles.workspace_role_permissions(workspace_two, new_user)
