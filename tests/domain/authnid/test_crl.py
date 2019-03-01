# Import installed packages
import pytest
import re
import os
import shutil
from datetime import datetime, timezone, timedelta
from OpenSSL import crypto, SSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

from atst.domain.authnid.crl import CRLCache, CRLRevocationException, NoOpCRLCache

from tests.mocks import FIXTURE_EMAIL_ADDRESS, DOD_CN


def rsa_key():
    return rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )


@pytest.fixture
def ca_key():
    return rsa_key()


@pytest.fixture
def make_x509():
    def _make_x509(private_key, signer_key=None, cn="ATAT", signer_cn="ATAT"):
        if signer_key is None:
            signer_key = private_key

        one_day = timedelta(1, 0, 0)
        public_key = private_key.public_key()
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        )
        builder = builder.issuer_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, signer_cn)])
        )
        if signer_key == private_key:
            builder = builder.add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            )
        builder = builder.not_valid_before(datetime.today() - (one_day * 2))
        builder = builder.not_valid_after(datetime.today() + (one_day * 30))
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(public_key)
        certificate = builder.sign(
            private_key=signer_key, algorithm=hashes.SHA256(), backend=default_backend()
        )

        return certificate

    return _make_x509


@pytest.fixture
def make_crl():
    def _make_crl(private_key, last_update_days=-1, next_update_days=30, cn="ATAT"):
        one_day = timedelta(1, 0, 0)
        builder = x509.CertificateRevocationListBuilder()
        builder = builder.issuer_name(
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])
        )
        builder = builder.last_update(datetime.today() + (one_day * last_update_days))
        builder = builder.next_update(datetime.today() + (one_day * next_update_days))
        crl = builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
            backend=default_backend(),
        )

        return crl

    return _make_crl


def serialize_pki_object_to_disk(obj, name, encoding=Encoding.PEM):
    with open(name, "wb") as file_:
        file_.write(obj.public_bytes(encoding))

        return name


@pytest.fixture
def ca_file(make_x509, ca_key, tmpdir):
    ca = make_x509(ca_key)
    ca_out = tmpdir.join("atat-ca.crt")
    serialize_pki_object_to_disk(ca, ca_out)

    return ca_out


@pytest.fixture
def expired_crl_file(make_crl, ca_key, tmpdir):
    crl = make_crl(ca_key, last_update_days=-7, next_update_days=-1)
    crl_out = tmpdir.join("atat-expired.crl")
    serialize_pki_object_to_disk(crl, crl_out, encoding=Encoding.DER)

    return crl_out


@pytest.fixture
def crl_file(make_crl, ca_key, tmpdir):
    crl = make_crl(ca_key)
    crl_out = tmpdir.join("atat-valid.crl")
    serialize_pki_object_to_disk(crl, crl_out, encoding=Encoding.DER)

    return crl_out


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


def test_can_build_crl_list(ca_file, ca_key, make_crl, tmpdir):
    crl = make_crl(ca_key)
    crl_file = tmpdir.join("atat.crl")
    serialize_pki_object_to_disk(crl, crl_file, encoding=Encoding.DER)

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


def test_updates_expired_certs(ca_file, expired_crl_file, crl_file, ca_key, make_x509):
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
