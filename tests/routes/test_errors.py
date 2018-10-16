
def test_csrf_error(app, client):
    app.config.update({"WTF_CSRF_ENABLED": True})

    response = client.post(
        "/requests/new/1",
        headers={ "Content-Type": "application/x-www-form-urlencoded" },
        data="csrf_token=invalid_token",
        follow_redirects=True,
    )

    body = response.data.decode()
    assert "Session Expired" in body
    assert "Log in Required" in body
