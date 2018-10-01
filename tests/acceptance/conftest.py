import os
import pytest
import logging
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .live_server import LiveServer


@pytest.fixture(scope="session")
def live_app(app):
    handler = RotatingFileHandler('log/acceptance.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    runnable = LiveServer(app, port=8943, timeout=10)
    runnable.spawn_live_server()
    app.server_url = runnable.server_url

    yield app

    runnable.terminate()


@pytest.fixture(scope="session")
def browserstack_config():
    return {
        "win7_ie10": {
            "browser": "IE",
            "browser_version": "10.0",
            "os": "Windows",
            "os_version": "7",
            "resolution": "1024x768",
            "browserstack.local": True,
        },
        "iphone7": {
            'browserName': 'iPhone',
            'device': 'iPhone 7',
            'realMobile': 'true',
            'os_version': '10.3',
            "browserstack.local": True,
        }
    }


@pytest.fixture(scope="session")
def driver_builder(browserstack_config):
    def build_driver(config_key):
        return webdriver.Remote(
            command_executor="http://{}:{}@hub.browserstack.com:80/wd/hub".format(
                os.getenv("BROWSERSTACK_EMAIL"), os.getenv("BROWSERSTACK_TOKEN")
            ),
            desired_capabilities=browserstack_config.get(config_key),
        )

    return build_driver


@pytest.fixture(scope="session")
def ie10_driver(driver_builder):
    driver = driver_builder("win7_ie10")

    yield driver

    driver.quit()
