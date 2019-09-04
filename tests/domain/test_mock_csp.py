import pytest

from atst.domain.csp import MockCloudProvider

CREDENTIALS = MockCloudProvider()._auth_credentials

@pytest.fixture
def mock_csp():
    return MockCloudProvider(with_delay=False, with_failure=False)


def test_create_environment(mock_csp: MockCloudProvider):
    environment_id = mock_csp.create_environment(CREDENTIALS, {}, {})
    assert isinstance(environment_id, str)


def test_create_admin_user(mock_csp: MockCloudProvider):
    admin_user = mock_csp.create_atat_admin_user(CREDENTIALS, "env_id")
    assert isinstance(admin_user["id"], str)
    assert isinstance(admin_user["credentials"], dict)


def test_create_environment_baseline(mock_csp: MockCloudProvider):
    baseline = mock_csp.create_atat_admin_user(CREDENTIALS, "env_id")
    assert isinstance(baseline, dict)


def test_create_or_update_user(mock_csp: MockCloudProvider):
    user_dict = mock_csp.create_or_update_user(CREDENTIALS, {}, "csp_role_id")
    assert isinstance(user_dict["id"], str)


def test_suspend_user(mock_csp: MockCloudProvider):
    assert mock_csp.suspend_user(CREDENTIALS, "csp_user_id")


def test_delete_user(mock_csp: MockCloudProvider):
    assert mock_csp.delete_user(CREDENTIALS, "csp_user_id")
