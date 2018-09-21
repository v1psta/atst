from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.users import Users
from tests.factories import WorkspaceFactory, UserFactory


def test_can_create_new_workspace_user():
    workspace = WorkspaceFactory.create()
    new_user = UserFactory.create()

    workspace_user_dicts = [{"id": new_user.id, "workspace_role": "owner"}]
    workspace_users = WorkspaceUsers.add_many(workspace.id, workspace_user_dicts)

    assert workspace_users[0].user.id == new_user.id
    assert workspace_users[0].user.atat_role.name == new_user.atat_role.name
    assert workspace_users[0].workspace_role.role.name == new_user.workspace_roles[0].role.name


def test_can_update_existing_workspace_user():
    workspace = WorkspaceFactory.create()
    new_user = UserFactory.create()

    WorkspaceUsers.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "owner"}]
    )
    workspace_users = WorkspaceUsers.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "developer"}]
    )

    assert workspace_users[0].user.atat_role.name == new_user.atat_role.name
    assert workspace_users[0].workspace_role.role.name == new_user.workspace_roles[0].role.name
