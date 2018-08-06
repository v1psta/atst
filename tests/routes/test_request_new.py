import re
import pytest
import urllib
from tests.mocks import MOCK_USER
from tests.factories import RequestFactory

ERROR_CLASS = "alert--error"
MOCK_REQUEST = RequestFactory.create(
    creator=MOCK_USER["id"],
    body={
        "financial_verification": {
            "pe_id": "0203752A",
        },
    }
)


def test_submit_invalid_request_form(monkeypatch, client, user_session):
    user_session()
    response = client.post(
        "/requests/new/1",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="total_ram=5",
    )
    assert re.search(ERROR_CLASS, response.data.decode())


def test_submit_valid_request_form(monkeypatch, client, user_session):
    user_session()
    monkeypatch.setattr("atst.forms.request.RequestForm.validate", lambda s: True)

    response = client.post(
        "/requests/new/1",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="meaning=42",
    )
    assert "/requests/new/2" in response.headers.get("Location")
