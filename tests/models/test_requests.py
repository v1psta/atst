from tests.factories import RequestFactory, UserFactory
from atst.domain.requests import Requests, RequestStatus


def test_started_request_requires_mo_action():
    request = RequestFactory.create()
    assert Requests.action_required_by(request) == "mission_owner"


def test_pending_financial_requires_mo_action():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_FINANCIAL_VERIFICATION)

    assert Requests.action_required_by(request) == "mission_owner"


def test_pending_ccpo_approval_requires_ccpo():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_CCPO_APPROVAL)

    assert Requests.action_required_by(request) == "ccpo"


def test_request_has_creator():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)

    assert request.creator == user
