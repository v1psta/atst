import pytest
from .browsers import BROWSERSTACK_CONFIG


@pytest.mark.parametrize("browser_type", BROWSERSTACK_CONFIG.keys())
def test_can_get_title(browser_type, live_app, drivers):
    driver = drivers[browser_type]
    driver.get(live_app.server_url)
    assert "JEDI" in driver.title
