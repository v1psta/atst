import re
import pytest
import urllib
from tests.mocks import MOCK_USER, MOCK_REQUEST
from tests.factories import RequestFactory, UserFactory, RequestStatusEventFactory
from atst.domain.roles import Roles


ERROR_CLASS = "alert--error"

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


def test_owner_can_view_request(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=user.id)
    status = RequestStatusEventFactory.create(request_id=request.id)

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 200


def test_non_owner_cannot_view_request(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create()
    status = RequestStatusEventFactory.create(request_id=request.id)

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 404


def test_ccpo_can_view_request(client, user_session):
    ccpo = Roles.get("ccpo")
    user = UserFactory.create(atat_role=ccpo)
    user_session(user)
    request = RequestFactory.create()
    status = RequestStatusEventFactory.create(request_id=request.id)

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 200
