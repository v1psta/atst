from tests.factories import UserFactory, WorkspaceFactory
from atst.domain.workspaces import Workspaces


def test_user_with_workspaces_has_workspaces_nav(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "default")

    user_session(user)
    response = client.get("/home")
    assert b'href="/workspaces"' in response.data


def test_user_without_workspaces_has_no_workspaces_nav(client, user_session):
    user = UserFactory.create()
    user_session(user)
    response = client.get("/home")
    assert b'href="/workspaces"' not in response.data
