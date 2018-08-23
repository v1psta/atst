from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.users import Users
from tests.factories import WorkspaceFactory


def test_can_create_new_workspace_user():
    workspace = WorkspaceFactory.create()
    new_user = Users.create("developer")

    workspace_user_dicts = [{"id": new_user.id, "workspace_role": "owner"}]
    workspace_users = WorkspaceUsers.add_many(workspace.id, workspace_user_dicts)

    assert workspace_users[0].user.id == new_user.id
    assert workspace_users[0].user.atat_role.name == "developer"
    assert workspace_users[0].workspace_role.role.name == "owner"


def test_can_update_existing_workspace_user():
    workspace = WorkspaceFactory.create()
    new_user = Users.create("developer")

    WorkspaceUsers.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "owner"}]
    )
    workspace_users = WorkspaceUsers.add_many(
        workspace.id, [{"id": new_user.id, "workspace_role": "developer"}]
    )

    assert workspace_users[0].user.id == new_user.id
    assert workspace_users[0].workspace_role.role.name == "developer"
