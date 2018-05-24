import pytest
import tornado.web
from app import make_app

@pytest.fixture
def app():
    return make_app()

@pytest.mark.gen_test
def test_hello_world(http_client, base_url):
    response = yield http_client.fetch(base_url)
    assert response.code == 200
