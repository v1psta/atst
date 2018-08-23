import pytest


@pytest.mark.parametrize(
    "path",
    (
        "/",
        "/home",
        "/workspaces",
        "/requests",
        "/requests/new/1",
        "/users",
        "/reports",
        "/calculator",
    ),
)
def test_routes(path, client, user_session):
    user_session()

    response = client.get(path)
    assert response.status_code == 200
