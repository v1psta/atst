import pytest
from tests.factories import UserFactory, RequestFactory
from atst.models.request_status_event import RequestStatus


@pytest.mark.requests_workflow
def test_creator_pending_finver(client, user_session):
    request = RequestFactory.create_with_status(
        RequestStatus.PENDING_FINANCIAL_VERIFICATION
    )
    user_session(request.creator)
    response = client.get(
        "/requests/edit/{}".format(request.id), follow_redirects=False
    )
    assert "verify" in response.location


@pytest.mark.requests_workflow
def test_creator_pending_finver_changes(client, user_session):
    request = RequestFactory.create_with_status(
        RequestStatus.CHANGES_REQUESTED_TO_FINVER
    )
    user_session(request.creator)
    response = client.get(
        "/requests/edit/{}".format(request.id), follow_redirects=False
    )
    assert "verify" in response.location


@pytest.mark.requests_workflow
def test_creator_approved(client, user_session):
    request = RequestFactory.create_with_status(RequestStatus.APPROVED)
    user_session(request.creator)
    response = client.get(
        "/requests/edit/{}".format(request.id), follow_redirects=False
    )
    assert "details" in response.location


@pytest.mark.requests_workflow
def test_creator_approved(client, user_session):
    request = RequestFactory.create_with_status(RequestStatus.STARTED)
    user_session(request.creator)
    response = client.get(
        "/requests/edit/{}".format(request.id), follow_redirects=False
    )
    assert "new" in response.location


@pytest.mark.requests_workflow
def test_ccpo(client, user_session):
    ccpo = UserFactory.from_atat_role("ccpo")
    request = RequestFactory.create_with_status(RequestStatus.STARTED)
    user_session(ccpo)
    response = client.get(
        "/requests/edit/{}".format(request.id), follow_redirects=False
    )
    assert "approval" in response.location
