import re
import pytest
import urllib
from tests.mocks import MOCK_USER, MOCK_REQUEST
from tests.factories import RequestFactory, UserFactory
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
    request = RequestFactory.create(creator=user)

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 200


def test_non_owner_cannot_view_request(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create()

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 404


def test_ccpo_can_view_request(client, user_session):
    ccpo = Roles.get("ccpo")
    user = UserFactory.create(atat_role=ccpo)
    user_session(user)
    request = RequestFactory.create()

    response = client.get("/requests/new/1/{}".format(request.id), follow_redirects=True)

    assert response.status_code == 200


def test_nonexistent_request(client, user_session):
    user_session()
    response = client.get("/requests/new/1/foo", follow_redirects=True)

    assert response.status_code == 404


def test_creator_info_is_autopopulated(monkeypatch, client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=user, body={"information_about_you": {}})

    response = client.get("/requests/new/2/{}".format(request.id))
    body = response.data.decode()
    assert 'value="{}"'.format(user.first_name) in body
    assert 'value="{}"'.format(user.last_name) in body
    assert 'value="{}"'.format(user.email) in body


def test_creator_info_is_autopopulated_for_new_request(monkeypatch, client, user_session):
    user = UserFactory.create()
    user_session(user)

    response = client.get("/requests/new/2")
    body = response.data.decode()
    assert 'value="{}"'.format(user.first_name) in body
    assert 'value="{}"'.format(user.last_name) in body
    assert 'value="{}"'.format(user.email) in body


def test_non_creator_info_is_not_autopopulated(monkeypatch, client, user_session):
    user = UserFactory.create()
    creator = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=creator, body={"information_about_you": {}})

    response = client.get("/requests/new/2/{}".format(request.id))
    body = response.data.decode()
    assert not user.first_name in body
    assert not user.last_name in body
    assert not user.email in body
