from atst.routes.requests.index import RequestsIndex
from tests.factories import RequestFactory, UserFactory
from atst.domain.requests import Requests


def test_action_required_mission_owner():
    creator = UserFactory.create()
    requests = RequestFactory.create_batch(5, creator=creator)
    Requests.submit(requests[0])
    context = RequestsIndex(creator).execute()

    assert context['requests'][0]['action_required'] == False


def test_action_required_ccpo():
    creator = UserFactory.create()
    requests = RequestFactory.create_batch(5, creator=creator)
    Requests.submit(requests[0])

    ccpo = UserFactory.from_atat_role("ccpo")
    context = RequestsIndex(ccpo).execute()

    assert context['num_action_required'] == 1
