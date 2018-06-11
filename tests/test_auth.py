import pytest
import tornado.web


@pytest.mark.gen_test
def test_redirects_when_not_logged_in(http_client, base_url):
    response = yield http_client.fetch(
        base_url + "/home", raise_error=False, follow_redirects=False
    )
    assert response.code == 302
    assert response.error
    assert response.headers["Location"] == "/login"

@pytest.mark.gen_test
def test_login_with_valid_bearer_token(app, monkeypatch, http_client, base_url):
    monkeypatch.setattr("atst.handler.validate_login_token", lambda t: True)
    response = yield http_client.fetch(
        base_url + "/home", headers={"Cookie": "bearer-token=anything"}
    )
    assert response.headers['Set-Cookie'].startswith('atst')
    assert response.code == 200
    assert not response.error

@pytest.mark.gen_test
def test_login_with_via_dev_endpoint(app, monkeypatch, http_client, base_url):
    response = yield http_client.fetch(
        base_url + "/login-dev", raise_error=False, follow_redirects=False
    )
    assert response.headers['Set-Cookie'].startswith('atst')
    assert response.code == 302
    assert response.headers["Location"] == "/home"

@pytest.mark.gen_test
@pytest.mark.skip(reason="need to work out auth error user paths")
def test_login_with_invalid_bearer_token(monkeypatch, http_client, base_url):
    monkeypatch.setattr("atst.handler.validate_login_token", lambda t: False)
    response = yield http_client.fetch(
        base_url + "/home",
        raise_error=False,
        headers={"Cookie": "bearer-token=anything"},
    )
