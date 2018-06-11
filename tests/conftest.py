import pytest

from atst.app import make_app, make_config


@pytest.fixture
def app():
    config = make_config()
    return make_app(config)
