import pytest
from tests.mocks import MOCK_USER

ERROR_CLASS = "usa-input-error-message"
APPROVED_MOCK_REQUEST = {
    "status": "approved"
}

@pytest.mark.gen_test
def test_submit_reviewed_request(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.check_xsrf_cookie", lambda s: True
    )
    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/submit/1",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="",
        raise_error=False,
        follow_redirects=False
    )
    assert response.headers["Location"] == "/requests"


@pytest.mark.gen_test
def test_submit_autoapproved_reviewed_request(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_submit.RequestsSubmit.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr(
        "tests.mocks.MOCK_REQUEST", APPROVED_MOCK_REQUEST
    )
    # this just needs to send a known invalid form value
    response = yield http_client.fetch(
        base_url + "/requests/submit/1",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="",
        raise_error=False,
        follow_redirects=False
    )
    assert response.headers["Location"] == "/requests?modal=True"
