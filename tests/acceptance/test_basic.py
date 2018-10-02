import pytest
import requests
from flask import url_for
from urllib.parse import urljoin
from .browsers import BROWSERSTACK_CONFIG
from atst.domain.users import Users
import atst.domain.exceptions as exceptions
from tests.test_auth import _login

import cryptography.x509 as x509
from cryptography.hazmat.backends import default_backend


USER_CERT = "ssl/client-certs/atat.mil.crt"


@pytest.mark.parametrize("browser_type", BROWSERSTACK_CONFIG.keys())
@pytest.mark.usefixtures('live_server')
def test_can_get_title(browser_type, app, drivers):
    driver = drivers[browser_type]
    driver.get(url_for("atst.root", _external=True))
    assert "JEDI" in driver.title


def _get_common_name(cert_path):
    with open(USER_CERT, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
        common_names = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        return common_names[0].value


@pytest.fixture(scope="module")
def valid_user_from_cert():
    cn = _get_common_name(USER_CERT)
    cn_parts = cn.split(".")
    user_info = {
        "last_name": cn_parts[0],
        "first_name": cn_parts[1],
        "dod_id": cn_parts[-1],
        "atat_role_name": "developer",
    }
    return Users.get_or_create_by_dod_id(**user_info)


def _valid_login(client, driver):
    with open(USER_CERT) as cert:
        response = _login(client, cert=cert.read())
        cookie = [cookie for cookie in client.cookie_jar][0]
        driver.add_cookie(
            {
                "domain": None,
                "name": cookie.name,
                "value": cookie.value,
                "path": cookie.path,
                "secure": cookie.secure,
                "expiry": cookie.expires,
            }
        )


@pytest.mark.usefixtures('live_server')
def test_login(drivers, client, app, valid_user_from_cert):
    driver = drivers["win10_chrome62"]
    driver.get(url_for("atst.root", _external=True))
    cookie = _valid_login(client, driver)
    requests_page = url_for("requests.requests_form_new", screen=1, _external=True)
    driver.get(requests_page)
    user = valid_user_from_cert
    assert user.last_name in driver.page_source
