import pytest

from atst.domain.csp import MockCloudProvider

from tests.factories import EnvironmentFactory, EnvironmentRoleFactory, UserFactory

CREDENTIALS = MockCloudProvider(config={})._auth_credentials


@pytest.fixture
def mock_csp():
    return MockCloudProvider(config={}, with_delay=False, with_failure=False)


def test_create_environment(mock_csp: MockCloudProvider):
    environment = EnvironmentFactory.create()
    user = UserFactory.create()
    environment_id = mock_csp.create_environment(CREDENTIALS, user, environment)
    assert isinstance(environment_id, str)


def test_create_admin_user(mock_csp: MockCloudProvider):
    admin_user = mock_csp.create_atat_admin_user(CREDENTIALS, "env_id")
    assert isinstance(admin_user["id"], str)
    assert isinstance(admin_user["credentials"], dict)


def test_create_environment_baseline(mock_csp: MockCloudProvider):
    baseline = mock_csp.create_atat_admin_user(CREDENTIALS, "env_id")
    assert isinstance(baseline, dict)


def test_create_or_update_user(mock_csp: MockCloudProvider):
    env_role = EnvironmentRoleFactory.create()
    csp_user_id = mock_csp.create_or_update_user(CREDENTIALS, env_role, "csp_role_id")
    assert isinstance(csp_user_id, str)


def test_suspend_user(mock_csp: MockCloudProvider):
    assert mock_csp.suspend_user(CREDENTIALS, "csp_user_id")


def test_delete_user(mock_csp: MockCloudProvider):
    assert mock_csp.delete_user(CREDENTIALS, "csp_user_id")
