# Import installed packages
import pytest
import re
import os
import shutil
from OpenSSL import crypto, SSL
from atst.domain.authnid.crl import crl_check, CRLCache, CRLRevocationException
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
    cache = CRLCache('ssl/client-certs/client-ca.crt', crl_locations=[location], store_class=MockX509Store)
    assert len(cache.crl_cache.keys()) == 1


def test_can_build_trusted_root_list():
    location = 'ssl/server-certs/ca-chain.pem'
    cache = CRLCache(root_location=location, crl_locations=[], store_class=MockX509Store)
    with open(location) as f:
        content = f.read()
        assert len(cache.certificate_authorities.keys()) == content.count('BEGIN CERT')

def test_can_validate_certificate():
    cache = CRLCache('ssl/server-certs/ca-chain.pem', crl_locations=['ssl/client-certs/client-ca.der.crl'])
    good_cert = open('ssl/client-certs/atat.mil.crt', 'rb').read()
    bad_cert = open('ssl/client-certs/bad-atat.mil.crt', 'rb').read()
    assert crl_check(cache, good_cert)
    with pytest.raises(CRLRevocationException):
        crl_check(cache, bad_cert)

def test_can_dynamically_update_crls(tmpdir):
    crl_file = tmpdir.join('test.crl')
    shutil.copyfile('ssl/client-certs/client-ca.der.crl', crl_file)
    cache = CRLCache('ssl/server-certs/ca-chain.pem', crl_locations=[crl_file])
    cert = open('ssl/client-certs/atat.mil.crt', 'rb').read()
    assert crl_check(cache, cert)
    # override the original CRL with one that revokes atat.mil.crt
    shutil.copyfile('tests/fixtures/test.der.crl', crl_file)
    with pytest.raises(CRLRevocationException):
        assert crl_check(cache, cert)

def test_parse_disa_pki_list():
    with open('tests/fixtures/disa-pki.html') as disa:
        disa_html = disa.read()
        crl_list = util.crl_list_from_disa_html(disa_html)
        href_matches = re.findall('DOD(ROOT|EMAIL|ID)?CA', disa_html)
        assert len(crl_list) > 0
        assert len(crl_list) == len(href_matches)

class MockStreamingResponse():
    def __init__(self, content_chunks, code=200):
        self.content_chunks = content_chunks
        self.status_code = code

    def iter_content(self, chunk_size=0):
        return self.content_chunks

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

def test_write_crl(tmpdir, monkeypatch):
    monkeypatch.setattr('requests.get', lambda u, **kwargs: MockStreamingResponse([b'it worked']))
    crl = 'crl_1'
    assert util.write_crl(tmpdir, "random_target_dir", crl)
    assert [p.basename for p in tmpdir.listdir()] == [crl]
    assert [p.read() for p in tmpdir.listdir()] == ['it worked']

def test_skips_crl_if_it_has_not_been_modified(tmpdir, monkeypatch):
    monkeypatch.setattr('requests.get', lambda u, **kwargs: MockStreamingResponse([b'it worked'], 304))
    assert not util.write_crl(tmpdir, "random_target_dir", 'crl_file_name')
