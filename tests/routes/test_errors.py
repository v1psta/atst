import pytest
from flask import url_for


@pytest.fixture
def csrf_enabled_app(app):
    app.config.update({"WTF_CSRF_ENABLED": True})
    yield app
    app.config.update({"WTF_CSRF_ENABLED": False})


def test_csrf_error(csrf_enabled_app, client):
    response = client.post(
        url_for("users.user"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="csrf_token=invalid_token",
        follow_redirects=True,
    )

    body = response.data.decode()
    assert "Session Expired" in body
    assert "Log in Required" in body
