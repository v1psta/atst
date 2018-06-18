import pytest

from atst.app import make_app, make_deps, make_config
from tests.mocks import MockApiClient


@pytest.fixture
def app():
    TEST_DEPS = {
        'authz_client': MockApiClient('authz'),
        'requests_client': MockApiClient('requests'),
        'authnid_client': MockApiClient('authnid'),
    }

    config = make_config()
    deps = make_deps(config)
    deps.update(TEST_DEPS)

    return make_app(config, deps)
