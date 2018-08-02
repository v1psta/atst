import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.requests import Requests

from tests.factories import RequestFactory


@pytest.fixture()
def requests(session):
    return Requests()

@pytest.fixture(scope="function")
def new_request(session):
    created_request = RequestFactory.create()
    session.add(created_request)
    session.commit()

    return created_request


def test_can_get_request(requests, new_request):
    request = requests.get(new_request.id)

    assert request.id == new_request.id


def test_nonexistent_request_raises(requests):
    with pytest.raises(NotFoundError):
        requests.get(uuid4())


def test_auto_approve_less_than_1m(requests, new_request):
    new_request.body = {"details_of_use": {"dollar_value": 999999}}
    request = requests.submit(new_request)

    assert request.status == 'approved'


def test_dont_auto_approve_if_dollar_value_is_1m_or_above(requests, new_request):
    new_request.body = {"details_of_use": {"dollar_value": 1000000}}
    request = requests.submit(new_request)

    assert request.status == 'submitted'


def test_dont_auto_approve_if_no_dollar_value_specified(requests, new_request):
    new_request.body = {"details_of_use": {}}
    request = requests.submit(new_request)

    assert request.status == 'submitted'
