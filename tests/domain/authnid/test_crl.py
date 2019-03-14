# Import installed packages
import pytest
import re
import os
import shutil
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding

from atst.domain.authnid.crl import (
    CRLCache,
    CRLRevocationException,
    CRLInvalidException,
    NoOpCRLCache,
)

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


def test_can_build_crl_list(crl_file, ca_key, ca_file, make_crl, tmpdir):
    crl = make_crl(ca_key)
    cache = CRLCache(ca_file, crl_locations=[crl_file], store_class=MockX509Store)
    issuer_der = crl.issuer.public_bytes(default_backend())
    assert len(cache.crl_cache.keys()) == 1
    assert issuer_der in cache.crl_cache
    assert cache.crl_cache[issuer_der]["location"] == crl_file
    assert cache.crl_cache[issuer_der]["expires"] == crl.next_update


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


def test_can_dynamically_update_crls(
    ca_key,
    ca_file,
    crl_file,
    rsa_key,
    make_x509,
    make_crl,
    serialize_pki_object_to_disk,
):
    cache = CRLCache(ca_file, crl_locations=[crl_file])
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    assert cache.crl_check(client_pem)

    revoked_crl = make_crl(ca_key, expired_serials=[client_cert.serial_number])
    # override the original CRL with one that revokes client_cert
    serialize_pki_object_to_disk(revoked_crl, crl_file, encoding=Encoding.DER)

    with pytest.raises(CRLRevocationException):
        assert cache.crl_check(client_pem)


def test_throws_error_for_missing_issuer():
    cache = CRLCache("ssl/server-certs/ca-chain.pem", crl_locations=[])
    # this cert is self-signed, and so the application does not have a
    # corresponding CRL for it
    cert = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS), "rb").read()
    with pytest.raises(CRLInvalidException) as exc:
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


def test_expired_crl_raises_CRLInvalidException_with_failover_config_false(
    app, ca_file, expired_crl_file, ca_key, make_x509, rsa_key
):
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    crl_cache = CRLCache(ca_file, crl_locations=[expired_crl_file])
    with pytest.raises(CRLInvalidException):
        crl_cache.crl_check(client_pem)


def test_expired_crl_passes_with_failover_config_true(
    ca_file, expired_crl_file, ca_key, make_x509, rsa_key, crl_failover_open_app
):
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)
    crl_cache = CRLCache(ca_file, crl_locations=[expired_crl_file])

    assert crl_cache.crl_check(client_pem)


def test_updates_expired_certs(
    rsa_key, ca_file, expired_crl_file, crl_file, ca_key, make_x509
):
    """
    Given a CRLCache object with an expired CRL and a function for updating the
    CRLs, the CRLCache should run the update function before checking a
    certificate that requires the expired CRL.
    """
    client_cert = make_x509(rsa_key(), signer_key=ca_key, cn="chewbacca")
    client_pem = client_cert.public_bytes(Encoding.PEM)

    def _crl_update_func():
        shutil.copyfile(crl_file, expired_crl_file)

    crl_cache = CRLCache(
        ca_file, crl_locations=[expired_crl_file], crl_update_func=_crl_update_func
    )
    crl_cache.crl_check(client_pem)
