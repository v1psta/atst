import os
import pytest
import logging
from collections import Mapping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .browsers import BROWSERSTACK_CONFIG


@pytest.fixture(scope="function", autouse=True)
def session(db, request):
    """
    Override base test session
    """
    pass


class DriverCollection(Mapping):
    """
    Allows access to drivers with dictionary syntax. Keeps track of which ones
    have already been initialized. Allows teardown of all existing drivers.
    """

    def __init__(self):
        self._drivers = {}

    def __iter__(self):
        return iter(self._drivers)

    def __len__(self):
        return len(self._drivers)

    def __getitem__(self, name):
        if name in self._drivers:
            return self._drivers[name]

        elif name in BROWSERSTACK_CONFIG:
            self._drivers[name] = self._build_driver(name)
            return self._drivers[name]

        else:
            raise AttributeError("Driver {} not found".format(name))

    def _build_driver(self, config_key):
        return webdriver.Remote(
            command_executor="http://{}:{}@hub.browserstack.com:80/wd/hub".format(
                os.getenv("BROWSERSTACK_EMAIL"), os.getenv("BROWSERSTACK_TOKEN")
            ),
            desired_capabilities=BROWSERSTACK_CONFIG.get(config_key),
        )

    def teardown(self):
        for driver in self._drivers.values():
            driver.quit()


@pytest.fixture(scope="session")
def drivers():
    driver_collection = DriverCollection()

    yield driver_collection

    driver_collection.teardown()
