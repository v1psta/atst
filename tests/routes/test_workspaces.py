from atst.routes.workspaces import list_workspaces
from atst.domain.workspaces import Workspaces
from tests.factories import UserFactory, RequestFactory


def test_list_workspaces(user_session):
    request = RequestFactory.create()
    Workspaces.create(request)

    result = list_workspaces(request.creator)
    assert len(result["workspaces"]) == 1
