import pytest
from urllib.parse import urlencode
from .factories import UserFactory, RequestFactory

from atst.routes.requests.jedi_request_flow import JEDIRequestFlow
from atst.models.request_status_event import RequestStatus
from atst.domain.requests import Requests


@pytest.fixture
def screens(app):
    return JEDIRequestFlow(3).screens


def serialize_dates(data):
    if not data:
        return data

    dates = {
        k: v.strftime("%m/%d/%Y") for k, v in data.items() if hasattr(v, "strftime")
    }

    new_data = data.copy()
    new_data.update(dates)

    return new_data


def test_stepthrough_request_form(user_session, screens, client):
    user = UserFactory.create()
    user_session(user)
    mock_request = RequestFactory.create()
    mock_body = mock_request.body

    def post_form(url, redirects=False, data=""):
        return client.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
            follow_redirects=redirects,
        )

    def take_a_step(inc, req=None, data=None):
        req_url = "/requests/new/{}".format(inc)
        if req:
            req_url += "/" + req
        # we do it twice, with and without redirect, in order to get the
        # destination url
        prelim_resp = post_form(req_url, data=data)
        response = post_form(req_url, True, data=data)
        assert prelim_resp.status_code == 302
        return (prelim_resp.headers.get("Location"), response)

    # GET the initial form
    response = client.get("/requests/new/1")
    assert screens[0]["title"] in response.data.decode()

    # POST to each of the form pages up until review and submit
    req_id = None
    for i in range(1, len(screens)):
        # get appropriate form data to POST for this section
        section = screens[i - 1]["section"]
        massaged = serialize_dates(mock_body[section])
        post_data = urlencode(massaged)

        effective_url, resp = take_a_step(i, req=req_id, data=post_data)
        req_id = effective_url.split("/")[-1]
        screen_title = screens[i]["title"].replace("&", "&amp;")

        assert "/requests/new/{}/{}".format(i + 1, req_id) in effective_url
        assert screen_title in resp.data.decode()

    # at this point, the real request we made and the mock_request bodies
    # should be equivalent
    assert Requests.get(user, req_id).body == mock_body

    # finish the review and submit step
    client.post(
        "/requests/submit/{}".format(req_id),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    finished_request = Requests.get(user, req_id)
    assert finished_request.status == RequestStatus.PENDING_CCPO_ACCEPTANCE
