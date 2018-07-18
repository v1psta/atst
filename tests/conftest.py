import pytest

from atst.app import make_app, make_deps, make_config
from tests.mocks import MockApiClient, MockRequestsClient, MockAuthzClient
from atst.sessions import DictSessions


@pytest.fixture
def app():
    TEST_DEPS = {
        "authz_client": MockAuthzClient("authz"),
        "requests_client": MockRequestsClient("requests"),
        "authnid_client": MockApiClient("authnid"),
        "sessions": DictSessions(),
    }

    config = make_config()
    deps = make_deps(config)
    deps.update(TEST_DEPS)

    return make_app(config, deps)

class DummyForm(dict):
    pass


class DummyField(object):
    def __init__(self, data=None, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def dummy_field():
    return DummyField()
