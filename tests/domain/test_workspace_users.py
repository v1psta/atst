from uuid import uuid4

from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.users import Users


def test_can_create_new_workspace_user():
    workspace_id = uuid4()
    user = Users.create("developer")

    workspace_user_dicts = [{"id": user.id, "workspace_role": "owner"}]

    workspace_users = WorkspaceUsers.add_many(workspace_id, workspace_user_dicts)

    assert workspace_users[0].user.id == user.id
    assert workspace_users[0].user.atat_role.name == "developer"
    assert workspace_users[0].workspace_role.role.name == "owner"


def test_can_update_existing_workspace_user():
    workspace_id = uuid4()
    user = Users.create("developer")

    WorkspaceUsers.add_many(
        workspace_id, [{"id": user.id, "workspace_role": "owner"}]
    )
    workspace_users = WorkspaceUsers.add_many(
        workspace_id, [{"id": user.id, "workspace_role": "developer"}]
    )

    assert workspace_users[0].user.id == user.id
    assert workspace_users[0].workspace_role.role.name == "developer"
