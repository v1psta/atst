import pytest
import tornado
from tests.mocks import MOCK_USER
from atst.handlers.request_new import JEDIRequestFlow

SCREENS = JEDIRequestFlow(None, None, 3).screens


@pytest.mark.gen_test
def test_stepthrough_request_form(monkeypatch, http_client, base_url):
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.get_current_user", lambda s: MOCK_USER
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.RequestNew.check_xsrf_cookie", lambda s: True
    )
    monkeypatch.setattr(
        "atst.handlers.request_new.JEDIRequestFlow.validate", lambda s: True
    )

    @tornado.gen.coroutine
    def take_a_step(inc, req=None):
        req_url = base_url + "/requests/new/{}".format(inc)
        if req:
            req_url += "/" + req
        response = yield http_client.fetch(
            req_url,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body="meaning=42",
        )
        return response

    # GET the initial form
    response = yield http_client.fetch(base_url + "/requests/new", method="GET")
    assert SCREENS[0]["title"] in response.body.decode()

    # POST to each of the form pages up until review and submit
    req_id = None
    for i in range(1, len(SCREENS)):
        resp = yield take_a_step(i, req=req_id)
        req_id = resp.effective_url.split("/")[-1]
        screen_title = SCREENS[i]["title"].replace("&", "&amp;")

        assert "/requests/new/{}/{}".format(i + 1, req_id) in resp.effective_url
        assert screen_title in resp.body.decode()
