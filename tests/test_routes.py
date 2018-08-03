def test_routes(client):
    for path in (
        "/",
        "/home",
        "/workspaces",
        "/requests",
        "/requests/new",
        "/requests/new/2",
        "/users",
        "/reports",
        "/calculator",
    ):
        response = client.get(path)
        if response.status_code == 404:
            __import__('ipdb').set_trace()
        assert response.status_code == 200
