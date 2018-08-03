from flask import session


MOCK_USER = {"id": "438567dd-25fa-4d83-a8cc-8aa8366cb24a"}
DOD_SDN_INFO = {
        'first_name': 'ART',
        'last_name': 'GARFUNKEL',
        'dod_id': '5892460358'
    }
DOD_SDN = f"CN={DOD_SDN_INFO['last_name']}.{DOD_SDN_INFO['first_name']}.G.{DOD_SDN_INFO['dod_id']},OU=OTHER,OU=PKI,OU=DoD,O=U.S. Government,C=US"


def _fetch_user_info(c, t):
    return MOCK_USER


def test_login(client, monkeypatch):
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
