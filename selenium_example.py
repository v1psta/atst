import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

desired_cap = {
 'browser': 'IE',
 'browser_version': '10.0',
 'os': 'Windows',
 'os_version': '7',
 'resolution': '1024x768',
 'browserstack.local': True
}

print("initializing the webdriver")
driver = webdriver.Remote(
    command_executor='http://{}:{}@hub.browserstack.com:80/wd/hub'.format(os.getenv("BROWSERSTACK_EMAIL"), os.getenv("BROWSERSTACK_TOKEN")),
    desired_capabilities=desired_cap)

print("fetching the localhost page")
driver.get("http://localhost:8000")
if not "JEDI" in driver.title:
    raise Exception("NO JEDI")
print("this is the page title: {}".format(driver.title))
driver.quit()
print("exiting")
