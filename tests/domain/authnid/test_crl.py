# Import installed packages
import pytest
import re
import os
import shutil
from OpenSSL import crypto, SSL
from atst.domain.authnid.crl.validator import Validator
import atst.domain.authnid.crl.util as util


class MockX509Store():
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
    location = 'ssl/client-certs/client-ca.der.crl'
    validator = Validator(crl_locations=[location], base_store=MockX509Store)
    assert len(validator.store.crls) == 1

def test_can_build_trusted_root_list():
    location = 'ssl/server-certs/ca-chain.pem'
    validator = Validator(roots=[location], base_store=MockX509Store)
    with open(location) as f:
        content = f.read()
        assert len(validator.store.certs) == content.count('BEGIN CERT')

def test_can_validate_certificate():
    validator = Validator(
            roots=['ssl/server-certs/ca-chain.pem'],
            crl_locations=['ssl/client-certs/client-ca.der.crl']
            )
    good_cert = open('ssl/client-certs/atat.mil.crt', 'rb').read()
    bad_cert = open('ssl/client-certs/bad-atat.mil.crt', 'rb').read()
    assert validator.validate(good_cert)
    assert validator.validate(bad_cert) == False

def test_can_dynamically_update_crls(tmpdir):
    crl_file = tmpdir.join('test.crl')
    shutil.copyfile('ssl/client-certs/client-ca.der.crl', crl_file)
    validator = Validator(
            roots=['ssl/server-certs/ca-chain.pem'],
            crl_locations=[crl_file]
            )
    cert = open('ssl/client-certs/atat.mil.crt', 'rb').read()
    assert validator.validate(cert)
    # override the original CRL with one that revokes atat.mil.crt
    shutil.copyfile('tests/fixtures/test.der.crl', crl_file)
    assert validator.validate(cert) == False

def test_parse_disa_pki_list():
    with open('tests/fixtures/disa-pki.html') as disa:
        disa_html = disa.read()
        crl_list = util.crl_list_from_disa_html(disa_html)
        href_matches = re.findall('DOD(ROOT|EMAIL|ID)?CA', disa_html)
        assert len(crl_list) > 0
        assert len(crl_list) == len(href_matches)

class MockStreamingResponse():
    def __init__(self, content_chunks):
        self.content_chunks = content_chunks

    def iter_content(self, chunk_size=0):
        return self.content_chunks

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

def test_write_crl(tmpdir, monkeypatch):
    monkeypatch.setattr('requests.get', lambda u, **kwargs: MockStreamingResponse([b'it worked']))
    crl = 'crl_1'
    util.write_crl(tmpdir, crl)
    assert [p.basename for p in tmpdir.listdir()] == [crl]
    assert [p.read() for p in tmpdir.listdir()] == ['it worked']
