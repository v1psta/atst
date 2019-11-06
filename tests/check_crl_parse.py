import os
import pytest

from atst.domain.authnid.crl.util import scan_for_issuer_and_next_update

from tests.utils import parse_for_issuer_and_next_update


CRL_DIR = "crls"
_CRLS = [
    "{}/{}".format(CRL_DIR, file_) for file_ in os.listdir(CRL_DIR) if ".crl" in file_
]


@pytest.mark.parametrize("crl_path", _CRLS)
def test_crl_scan_against_parse(crl_path):
    parsed_der = parse_for_issuer_and_next_update(crl_path)
    scanned_der = scan_for_issuer_and_next_update(crl_path)
    assert parsed_der == scanned_der
