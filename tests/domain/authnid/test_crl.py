# Import installed packages
import pytest
import re
import os
import shutil
from OpenSSL import crypto, SSL

from atst.domain.authnid.crl import CRLCache, CRLRevocationException, NoOpCRLCache

from tests.mocks import FIXTURE_EMAIL_ADDRESS, DOD_CN


class MockX509Store:
    def __init__(self):
        self.crls = []
        self.certs = []

    def add_crl(self, crl):
        self.crls.append(crl)

    def add_cert(self, cert):
        self.certs.append(cert)

    def set_flags(self, flag):
        pass


def test_can_build_crl_list(monkeypatch):
    location = "ssl/client-certs/client-ca.der.crl"
    cache = CRLCache(
        "ssl/client-certs/client-ca.crt",
        crl_locations=[location],
        store_class=MockX509Store,
    )
    assert len(cache.crl_cache.keys()) == 1


def test_can_build_trusted_root_list():
    location = "ssl/server-certs/ca-chain.pem"
    cache = CRLCache(
        root_location=location, crl_locations=[], store_class=MockX509Store
    )
    with open(location) as f:
        content = f.read()
        assert len(cache.certificate_authorities.keys()) == content.count("BEGIN CERT")


def test_can_build_crl_list_with_missing_crls():
    location = "ssl/client-certs/client-ca.der.crl"
    cache = CRLCache(
        "ssl/client-certs/client-ca.crt",
        crl_locations=["tests/fixtures/sample.pdf"],
        store_class=MockX509Store,
    )
    assert len(cache.crl_cache.keys()) == 0


def test_can_validate_certificate():
    cache = CRLCache(
        "ssl/server-certs/ca-chain.pem",
        crl_locations=["ssl/client-certs/client-ca.der.crl"],
    )
    good_cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    bad_cert = open("ssl/client-certs/bad-atat.mil.crt", "rb").read()
    assert cache.crl_check(good_cert)
    with pytest.raises(CRLRevocationException):
        cache.crl_check(bad_cert)


def test_can_dynamically_update_crls(tmpdir):
    crl_file = tmpdir.join("test.crl")
    shutil.copyfile("ssl/client-certs/client-ca.der.crl", crl_file)
    cache = CRLCache("ssl/server-certs/ca-chain.pem", crl_locations=[crl_file])
    cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    assert cache.crl_check(cert)
    # override the original CRL with one that revokes atat.mil.crt
    shutil.copyfile("tests/fixtures/test.der.crl", crl_file)
    with pytest.raises(CRLRevocationException):
        assert cache.crl_check(cert)


def test_throws_error_for_missing_issuer():
    cache = CRLCache("ssl/server-certs/ca-chain.pem", crl_locations=[])
    # this cert is self-signed, and so the application does not have a
    # corresponding CRL for it
    cert = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS), "rb").read()
    with pytest.raises(CRLRevocationException) as exc:
        assert cache.crl_check(cert)
    (message,) = exc.value.args
    # objects that the issuer is missing
    assert "issuer" in message
    # names the issuer we were expecting to find a CRL for; same as the
    # certificate subject in this case because the cert is self-signed
    assert DOD_CN in message


def test_multistep_certificate_chain():
    cache = CRLCache(
        "tests/fixtures/chain/ca-chain.pem",
        crl_locations=["tests/fixtures/chain/intermediate.crl"],
    )
    cert = open("tests/fixtures/chain/client.crt", "rb").read()
    assert cache.crl_check(cert)


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(msg)

    def warning(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def test_no_op_crl_cache_logs_common_name():
    logger = FakeLogger()
    cert = open("ssl/client-certs/atat.mil.crt", "rb").read()
    cache = NoOpCRLCache(logger=logger)
    assert cache.crl_check(cert)
    assert "ART.GARFUNKEL.1234567890" in logger.messages[-1]
