import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.requests import Requests
from atst.models.request_status_event import RequestStatus

from tests.factories import RequestFactory, UserFactory


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
