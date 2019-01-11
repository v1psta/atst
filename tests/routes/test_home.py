import pytest

from tests.factories import UserFactory, WorkspaceFactory, RequestFactory
from atst.domain.workspaces import Workspaces


def test_user_with_workspaces_has_workspaces_nav(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.get("/home", follow_redirects=True)
    assert b'href="/workspaces"' in response.data


@pytest.mark.skip(reason="this may no longer be accurate")
def test_user_without_workspaces_has_no_workspaces_nav(client, user_session):
    user = UserFactory.create()
    user_session(user)
    response = client.get("/home", follow_redirects=True)
    assert b'href="/workspaces"' not in response.data


@pytest.mark.skip(reason="this may no longer be accurate")
def test_request_owner_with_no_workspaces_redirected_to_requests(client, user_session):
    request = RequestFactory.create()
    user_session(request.creator)
    response = client.get("/home", follow_redirects=False)

    assert "/requests" in response.location


def test_request_owner_with_one_workspace_redirected_to_reports(client, user_session):
    request = RequestFactory.create()
    workspace = Workspaces.create_from_request(request)

    user_session(request.creator)
    response = client.get("/home", follow_redirects=False)

    assert "/workspaces/{}/reports".format(workspace.id) in response.location


def test_request_owner_with_more_than_one_workspace_redirected_to_workspaces(
    client, user_session
):
    request_creator = UserFactory.create()
    Workspaces.create_from_request(RequestFactory.create(creator=request_creator))
    Workspaces.create_from_request(RequestFactory.create(creator=request_creator))

    user_session(request_creator)
    response = client.get("/home", follow_redirects=False)

    assert "/workspaces" in response.location


@pytest.mark.skip(reason="this may no longer be accurate")
def test_non_owner_user_with_no_workspaces_redirected_to_requests(client, user_session):
    user = UserFactory.create()

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/requests" in response.location


def test_non_owner_user_with_one_workspace_redirected_to_workspace_projects(
    client, user_session
):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/workspaces/{}/projects".format(workspace.id) in response.location


def test_non_owner_user_with_mulitple_workspaces_redirected_to_workspaces(
    client, user_session
):
    user = UserFactory.create()
    for _ in range(3):
        workspace = WorkspaceFactory.create()
        Workspaces._create_workspace_role(user, workspace, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/workspaces" in response.location


@pytest.mark.skip(reason="this may no longer be accurate")
def test_ccpo_user_redirected_to_requests(client, user_session):
    user = UserFactory.from_atat_role("ccpo")
    for _ in range(3):
        workspace = WorkspaceFactory.create()
        Workspaces._create_workspace_role(user, workspace, "developer")

    user_session(user)
    response = client.get("/home", follow_redirects=False)

    assert "/requests" in response.location
