import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.requests import Requests
from atst.models.request import Request
from atst.models.request_status_event import RequestStatus

from tests.factories import RequestFactory, UserFactory, RequestStatusEventFactory


@pytest.fixture(scope="function")
def new_request(session):
    return RequestFactory.create()


def test_can_get_request(new_request):
    request = Requests.get(new_request.id)

    assert request.id == new_request.id


def test_nonexistent_request_raises():
    with pytest.raises(NotFoundError):
        Requests.get(uuid4())


def test_new_request_has_started_status():
    request = Requests.create(UserFactory.build(), {})
    assert request.status == RequestStatus.STARTED


def test_auto_approve_less_than_1m(new_request):
    new_request.body = {"details_of_use": {"dollar_value": 999999}}
    request = Requests.submit(new_request)

    assert request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION


def test_dont_auto_approve_if_dollar_value_is_1m_or_above(new_request):
    new_request.body = {"details_of_use": {"dollar_value": 1000000}}
    request = Requests.submit(new_request)

    assert request.status == RequestStatus.PENDING_CCPO_APPROVAL


def test_dont_auto_approve_if_no_dollar_value_specified(new_request):
    new_request.body = {"details_of_use": {}}
    request = Requests.submit(new_request)

    assert request.status == RequestStatus.PENDING_CCPO_APPROVAL


def test_should_allow_submission(new_request):
    assert Requests.should_allow_submission(new_request)

    RequestStatusEventFactory.create(request=new_request, new_status=RequestStatus.CHANGES_REQUESTED)
    assert Requests.should_allow_submission(new_request)

    del new_request.body['details_of_use']
    assert not Requests.should_allow_submission(new_request)


def test_exists(session):
    user_allowed = UserFactory.create()
    user_denied = UserFactory.create()
    request = RequestFactory.create(creator=user_allowed)
    assert Requests.exists(request.id, user_allowed)
    assert not Requests.exists(request.id, user_denied)


def test_status_count(session):
    # make sure table is empty
    session.query(Request).delete()

    request1 = RequestFactory.create()
    request2 = RequestFactory.create()
    RequestStatusEventFactory.create(sequence=2, request_id=request2.id, new_status=RequestStatus.PENDING_FINANCIAL_VERIFICATION)

    assert Requests.status_count(RequestStatus.PENDING_FINANCIAL_VERIFICATION) == 1
    assert Requests.status_count(RequestStatus.STARTED) == 1
    assert Requests.in_progress_count() == 2

def test_status_count_scoped_to_creator(session):
    # make sure table is empty
    session.query(Request).delete()

    user = UserFactory.create()
    request1 = RequestFactory.create()
    request2 = RequestFactory.create(creator=user)

    assert Requests.status_count(RequestStatus.STARTED) == 2
    assert Requests.status_count(RequestStatus.STARTED, creator=user) == 1
