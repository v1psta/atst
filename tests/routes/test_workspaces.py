from flask import url_for

from tests.factories import WorkspaceFactory


def test_update_workspace_name(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.post(
        url_for("workspaces.edit_workspace", workspace_id=workspace.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert workspace.name == "a cool new name"
