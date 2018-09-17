from flask import url_for

from tests.factories import UserFactory, WorkspaceFactory
from atst.domain.workspaces import Workspaces
from atst.models.workspace_user import WorkspaceUser


def test_user_with_permission_has_add_project_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "owner")

    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_project_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        not in response.data
    )


def test_user_with_permission_has_add_member_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "owner")

    user_session(user)
    response = client.get("/workspaces/{}/members".format(workspace.id))
    assert (
        'href="/workspaces/{}/members/new"'.format(workspace.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_member_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    user_session(user)
    response = client.get("/workspaces/{}/members".format(workspace.id))
    assert (
        'href="/workspaces/{}/members/new"'.format(workspace.id).encode()
        not in response.data
    )


def test_update_workspace_name(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "admin")
    user_session(user)
    response = client.post(
        url_for("workspaces.edit_workspace", workspace_id=workspace.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert workspace.name == "a cool new name"
