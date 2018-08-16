import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.workspaces import Workspaces

from tests.factories import WorkspaceFactory, RequestFactory, TaskOrderFactory


def test_can_create_workspace():
    request = RequestFactory.create()
    to = TaskOrderFactory.create()
    workspace = Workspaces.create(request, to)
    assert workspace.request == request
    assert workspace.task_order == to
    assert workspace.name == request.id

    workspace = Workspaces.create(request, to, name="frugal-whale")
    assert workspace.name == "frugal-whale"


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
