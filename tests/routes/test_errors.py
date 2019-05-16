import pytest
from flask import url_for

from tests.factories import TaskOrderFactory


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
    assert "Log in required" in body


def test_portfolio_route_without_user_session(csrf_enabled_app, client):
    task_order = TaskOrderFactory.create()

    endpoint_url = url_for("task_orders.update", task_order_id=task_order.id, screen=1)
    response = client.post(
        endpoint_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"csrf_token": "invalid_token"},
    )

    assert response.status_code == 302
    assert url_for("atst.root", next=endpoint_url) in response.location
