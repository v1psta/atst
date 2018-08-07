import pytest
from tests.mocks import MOCK_USER
from atst.routes.requests.jedi_request_flow import JEDIRequestFlow

@pytest.fixture
def screens(app):
    return JEDIRequestFlow(3).screens


@pytest.mark.skip()
def test_stepthrough_request_form(monkeypatch, screens, client):
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.JEDIRequestFlow.validate", lambda s: True
    )

    def take_a_step(inc, req=None):
        req_url = "/requests/new/{}".format(inc)
        if req:
            req_url += "/" + req
        response = client.post(
            req_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="meaning=42",
        )
        return response

    # GET the initial form
    response = client.get("/requests/new")
    assert screens[0]["title"] in response.data.decode()

    # POST to each of the form pages up until review and submit
    req_id = None
    for i in range(1, len(screens)):
        resp = take_a_step(i, req=req_id)
        __import__('ipdb').set_trace()
        req_id = resp.effective_url.split("/")[-1]
        screen_title = screens[i]["title"].replace("&", "&amp;")

        assert "/requests/new/{}/{}".format(i + 1, req_id) in resp.effective_url
        assert screen_title in resp.data.decode()
