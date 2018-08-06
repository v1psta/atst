from flask import session
from .mocks import DOD_SDN


MOCK_USER = {"id": "438567dd-25fa-4d83-a8cc-8aa8366cb24a"}


def _fetch_user_info(c, t):
    return MOCK_USER


def test_successful_login_redirect(client, monkeypatch):
    monkeypatch.setattr("atst.routes.is_valid_certificate", lambda *args: True)

    resp = client.get(
        "/login-redirect",
        environ_base={
            "HTTP_X_SSL_CLIENT_VERIFY": "SUCCESS",
            "HTTP_X_SSL_CLIENT_S_DN": DOD_SDN,
        },
    )

    assert resp.status_code == 302
    assert "home" in resp.headers["Location"]
    assert session["user_id"]


def test_unsuccessful_login_redirect(client, monkeypatch):
    resp = client.get("/login-redirect")

    assert resp.status_code == 302
    assert "unauthorized" in resp.headers["Location"]
    assert "user_id" not in session
