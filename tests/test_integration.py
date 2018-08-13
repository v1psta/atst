import pytest
from .factories import UserFactory
from atst.routes.requests.jedi_request_flow import JEDIRequestFlow

@pytest.fixture
def screens(app):
    return JEDIRequestFlow(3).screens


def test_stepthrough_request_form(monkeypatch, user_session, screens, client):
    user = UserFactory.create()
    user_session(user)

    monkeypatch.setattr(
        "atst.routes.requests.jedi_request_flow.JEDIRequestFlow.validate", lambda s: True
    )

    def post_form(url, redirects=False):
         return client.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="meaning=42",
            follow_redirects=redirects
        )


    def take_a_step(inc, req=None):
        req_url = "/requests/new/{}".format(inc)
        if req:
            req_url += "/" + req
        # we do it twice, with and without redirect, in order to get the
        # destination url
        prelim_resp = post_form(req_url)
        response = post_form(req_url, True)
        return (prelim_resp.headers.get("Location"), response)

    # GET the initial form
    response = client.get("/requests/new/1")
    assert screens[0]["title"] in response.data.decode()

    # POST to each of the form pages up until review and submit
    req_id = None
    for i in range(1, len(screens)):
        effective_url, resp = take_a_step(i, req=req_id)
        req_id = effective_url.split("/")[-1]
        screen_title = screens[i]["title"].replace("&", "&amp;")

        assert "/requests/new/{}/{}".format(i + 1, req_id) in effective_url
        assert screen_title in resp.data.decode()
