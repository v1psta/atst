import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers

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


def test_can_get_workspace():
    workspace = WorkspaceFactory.create()
    found = Workspaces.get(workspace.id)
    assert workspace == found


def test_nonexistent_workspace_raises():
    with pytest.raises(NotFoundError):
        Workspaces.get(uuid4())


def test_can_get_workspace_by_request():
    workspace = WorkspaceFactory.create()
    found = Workspaces.get_by_request(workspace.request)
    assert workspace == found


def test_creating_workspace_adds_owner():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    workspace = Workspaces.create(request)
    workspace_user = WorkspaceUsers.get(workspace.id, user.id)
    assert workspace_user.workspace_role


def test_workspace_has_timestamps():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.time_created == workspace.time_updated


def test_workspace_has_roles():
    request = RequestFactory.create()
    workspace = Workspaces.create(request)
    assert workspace.roles[0].user == request.creator
