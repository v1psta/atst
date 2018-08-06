import pytest

@pytest.mark.parametrize("path", (
        "/",
        "/home",
        "/workspaces",
        "/requests",
        "/requests/new",
        "/requests/new/2",
        "/users",
        "/reports",
        "/calculator",
    ))
def test_routes(path, client, monkeypatch):
    monkeypatch.setattr("atst.domain.auth.get_current_user", lambda *args: True)

    response = client.get(path)
    assert response.status_code == 200
