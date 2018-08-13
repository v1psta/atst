import pytest
from tests.mocks import MOCK_USER
from tests.factories import RequestFactory
from atst.models.request_status_event import RequestStatus


def _mock_func(*args, **kwargs):
    return RequestFactory.create()


def test_submit_reviewed_request(monkeypatch, client, user_session):
    user_session()
    monkeypatch.setattr("atst.domain.requests.Requests.get", _mock_func)
    monkeypatch.setattr("atst.domain.requests.Requests.submit", _mock_func)
    monkeypatch.setattr("atst.models.request.Request.status", "pending")
    # this just needs to send a known invalid form value
    response = client.post(
        "/requests/submit/1",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="",
        follow_redirects=False,
    )
    assert "/requests" in response.headers["Location"]
    assert "modal=pendingCCPOApproval" in response.headers["Location"]


def test_submit_autoapproved_reviewed_request(monkeypatch, client, user_session):
    user_session()
    monkeypatch.setattr("atst.domain.requests.Requests.get", _mock_func)
    monkeypatch.setattr("atst.domain.requests.Requests.submit", _mock_func)
    monkeypatch.setattr("atst.models.request.Request.status", RequestStatus.PENDING_FINANCIAL_VERIFICATION)
    response = client.post(
        "/requests/submit/1",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="",
        follow_redirects=False,
    )
    assert "/requests?modal=pendingFinancialVerification" in response.headers["Location"]
