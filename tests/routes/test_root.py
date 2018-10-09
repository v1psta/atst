from tests.factories import UserFactory


def test_root_redirects_if_user_is_logged_in(client, user_session):
    user_session(UserFactory.create())
    response = client.get("/", follow_redirects=False)
    assert "home" in response.location
