import pytest

from atst.domain.csp import MockCloudProvider


@pytest.fixture
def mock_csp():
    return MockCloudProvider(with_delay=False, with_failure=False)


def test_create_environment(mock_csp: MockCloudProvider):
    credentials = mock_csp._auth_credentials()
    environment_id = mock_csp.create_environment(credentials, {}, {})
    assert isinstance(environment_id, str)
