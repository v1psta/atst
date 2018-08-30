import re
from tests.factories import RequestFactory, UserFactory, RequestRevisionFactory
from atst.domain.roles import Roles
from atst.domain.requests import Requests
from urllib.parse import urlencode

from tests.assert_util import dict_contains

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

    response = client.get(
        "/requests/new/1/{}".format(request.id), follow_redirects=True
    )

    assert response.status_code == 200


def test_non_owner_cannot_view_request(client, user_session):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create()

    response = client.get(
        "/requests/new/1/{}".format(request.id), follow_redirects=True
    )

    assert response.status_code == 404


def test_ccpo_can_view_request(client, user_session):
    ccpo = Roles.get("ccpo")
    user = UserFactory.create(atat_role=ccpo)
    user_session(user)
    request = RequestFactory.create()

    response = client.get(
        "/requests/new/1/{}".format(request.id), follow_redirects=True
    )

    assert response.status_code == 200


def test_nonexistent_request(client, user_session):
    user_session()
    response = client.get("/requests/new/1/foo", follow_redirects=True)

    assert response.status_code == 404


def test_creator_info_is_autopopulated_for_existing_request(
    monkeypatch, client, user_session
):
    user = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=user, initial_revision={})

    response = client.get("/requests/new/2/{}".format(request.id))
    body = response.data.decode()
    assert "initial-value='{}'".format(user.first_name) in body
    assert "initial-value='{}'".format(user.last_name) in body
    assert "initial-value='{}'".format(user.email) in body


def test_creator_info_is_autopopulated_for_new_request(
    monkeypatch, client, user_session
):
    user = UserFactory.create()
    user_session(user)

    response = client.get("/requests/new/2")
    body = response.data.decode()
    assert "initial-value='{}'".format(user.first_name) in body
    assert "initial-value='{}'".format(user.last_name) in body
    assert "initial-value='{}'".format(user.email) in body


def test_non_creator_info_is_not_autopopulated(monkeypatch, client, user_session):
    user = UserFactory.create()
    creator = UserFactory.create()
    user_session(user)
    request = RequestFactory.create(creator=creator, initial_revision={})

    response = client.get("/requests/new/2/{}".format(request.id))
    body = response.data.decode()
    assert not user.first_name in body
    assert not user.last_name in body
    assert not user.email in body


def test_am_poc_causes_poc_to_be_autopopulated(client, user_session):
    creator = UserFactory.create()
    user_session(creator)
    request = RequestFactory.create(creator=creator, initial_revision={})
    client.post(
        "/requests/new/3/{}".format(request.id),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="am_poc=yes",
    )
    request = Requests.get(creator, request.id)
    assert request.body["primary_poc"]["dodid_poc"] == creator.dod_id


def test_not_am_poc_requires_poc_info_to_be_completed(client, user_session):
    creator = UserFactory.create()
    user_session(creator)
    request = RequestFactory.create(creator=creator, initial_revision={})
    response = client.post(
        "/requests/new/3/{}".format(request.id),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="am_poc=no",
        follow_redirects=True,
    )
    assert ERROR_CLASS in response.data.decode()


def test_not_am_poc_allows_user_to_fill_in_poc_info(client, user_session):
    creator = UserFactory.create()
    user_session(creator)
    request = RequestFactory.create(creator=creator, initial_revision={})
    poc_input = {
        "am_poc": "no",
        "fname_poc": "test",
        "lname_poc": "user",
        "email_poc": "test.user@mail.com",
        "dodid_poc": "1234567890",
    }
    response = client.post(
        "/requests/new/3/{}".format(request.id),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=urlencode(poc_input),
    )
    assert ERROR_CLASS not in response.data.decode()


def test_poc_details_can_be_autopopulated_on_new_request(client, user_session):
    creator = UserFactory.create()
    user_session(creator)
    response = client.post(
        "/requests/new/3",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="am_poc=yes",
    )
    request_id = response.headers["Location"].split("/")[-1]
    request = Requests.get(creator, request_id)

    assert request.body["primary_poc"]["dodid_poc"] == creator.dod_id


def test_poc_autofill_checks_information_about_you_form_first(client, user_session):
    creator = UserFactory.create()
    user_session(creator)
    request = RequestFactory.create(
        creator=creator,
        initial_revision=dict(
            fname_request="Alice",
            lname_request="Adams",
            email_request="alice.adams@mail.mil",
        ),
    )
    poc_input = {"am_poc": "yes"}
    client.post(
        "/requests/new/3/{}".format(request.id),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=urlencode(poc_input),
    )
    request = Requests.get(creator, request.id)
    assert dict_contains(
        request.body["primary_poc"],
        {
            "fname_poc": "Alice",
            "lname_poc": "Adams",
            "email_poc": "alice.adams@mail.mil",
        },
    )


def test_can_review_data(user_session, client):
    creator = UserFactory.create()
    user_session(creator)
    request = RequestFactory.create(creator=creator)
    response = client.get("/requests/new/4/{}".format(request.id))
    body = response.data.decode()
    # assert a sampling of the request data is on the review page
    assert request.body["primary_poc"]["fname_poc"] in body
    assert request.body["information_about_you"]["email_request"] in body
