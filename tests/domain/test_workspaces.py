import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError, UnauthorizedError
from atst.domain.workspaces import Workspaces

from tests.factories import WorkspaceFactory, RequestFactory, UserFactory


def test_can_create_workspace():
    request = RequestFactory.create()
    workspace = Workspaces.create(request, name="frugal-whale")
    assert workspace.name == "frugal-whale"
    assert workspace.request == request


def test_default_workspace_name_is_request_id():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.name == str(request.id)


def test_get_nonexistent_workspace_raises():
    with pytest.raises(NotFoundError):
        Workspaces.get(UserFactory.build(), uuid4())


def test_can_get_workspace_by_request():
    workspace = WorkspaceFactory.create()
    found = Workspaces.get_by_request(workspace.request)
    assert workspace == found


def test_creating_workspace_adds_owner():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    workspace = Workspaces.create(request)
    assert workspace.roles[0].user == user


def test_workspace_has_timestamps():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.time_created == workspace.time_updated


def test_workspaces_get_ensures_user_is_in_workspace():
    owner = UserFactory.create()
    outside_user = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))

    workspace_ = Workspaces.get(owner, workspace.id)
    assert workspace_ == workspace

    with pytest.raises(UnauthorizedError):
        Workspaces.get(outside_user, workspace.id)


def test_workspaces_get_many_with_no_workspaces():
    workspaces = Workspaces.get_many(UserFactory.build())
    assert workspaces == []


def test_workspaces_get_many_returns_a_users_workspaces():
    user = UserFactory.create()
    users_workspace = Workspaces.create(RequestFactory.create(creator=user))

    # random workspace
    Workspaces.create(RequestFactory.create())

    assert Workspaces.get_many(user) == [users_workspace]
