import pytest
from atst.domain.authnid.crl import CRLCache, CRLRevocationException
from atst.utils.pdf_verification import pdf_signature_validations


@pytest.fixture
def crl_check():
    def _crl_check(signers_cert):
        try:
            cache = CRLCache(
                "ssl/server-certs/ca-chain.pem",
                crl_locations=["ssl/client-certs/client-ca.der.crl"],
            )
            return cache.crl_check(signers_cert)
        except CRLRevocationException:
            return False

    return _crl_check


def test_unsigned_pdf(crl_check):
    unsigned_pdf = open("tests/fixtures/sample.pdf", "rb").read()
    result = pdf_signature_validations(pdf=unsigned_pdf, crl_check=crl_check)

    assert result == {"result": False, "signature_count": 0, "signatures": []}


def test_valid_signed_pdf(crl_check):
    valid_signed_pdf = open("tests/fixtures/sally-darth-signed.pdf", "rb").read()
    result = pdf_signature_validations(pdf=valid_signed_pdf, crl_check=crl_check)

    assert result == {
        "result": True,
        "signature_count": 2,
        "signatures": [
            {
                "cert_common_name": "WILLIAMS.SALLY.3453453453",
                "hashed_binary_data": "b879a15e19eece534dc63019d3fe539ff4a3efbf8e8f5403a8bdae26a9b713ea",
                "hashing_algorithm": "sha256",
                "is_valid": True,
                "is_valid_cert": True,
                "is_valid_hash": True,
                "is_valid_signature": True,
                "signers_serial": 9_662_248_800_192_484_626,
            },
            {
                "cert_common_name": "VADER.DARTH.9012345678",
                "hashed_binary_data": "d98339766c20a369219f236220d7b450111554acc902e242d015dd6d306c7809",
                "hashing_algorithm": "sha256",
                "is_valid": True,
                "is_valid_cert": True,
                "is_valid_hash": True,
                "is_valid_signature": True,
                "signers_serial": 9_662_248_800_192_484_627,
            },
        ],
    }


def test_signed_pdf_thats_been_modified(crl_check):
    valid_signed_pdf = open("tests/fixtures/sally-darth-signed.pdf", "rb").read()
    modified_pdf = valid_signed_pdf.replace(b"PDF-1.6", b"PDF-1.7")
    result = pdf_signature_validations(pdf=modified_pdf, crl_check=crl_check)

    assert result == {
        "result": False,
        "signature_count": 2,
        "signatures": [
            {
                "cert_common_name": "WILLIAMS.SALLY.3453453453",
                "hashed_binary_data": "d1fb3c955b57f139331586276ba4abca90ecc5d36b53fe6bbbbbd8707d7124bb",
                "hashing_algorithm": "sha256",
                "is_valid": False,
                "is_valid_cert": True,
                "is_valid_hash": False,
                "is_valid_signature": True,
                "signers_serial": 9_662_248_800_192_484_626,
            },
            {
                "cert_common_name": "VADER.DARTH.9012345678",
                "hashed_binary_data": "75ef47824de4b5477c75665c5a90e39a2b8a8985422cf2f7f641661a7b5217a8",
                "hashing_algorithm": "sha256",
                "is_valid": False,
                "is_valid_cert": True,
                "is_valid_hash": False,
                "is_valid_signature": True,
                "signers_serial": 9_662_248_800_192_484_627,
            },
        ],
    }


@pytest.mark.skip(reason="Need fixture file")
def test_signed_pdf_dod_revoked(crl_check):
    signed_pdf_dod_revoked = open(
        "tests/fixtures/signed-pdf-dod_revoked.pdf", "rb"
    ).read()
    result = pdf_signature_validations(pdf=signed_pdf_dod_revoked, crl_check=crl_check)

    assert result == {
        "result": False,
        "signature_count": 1,
        "signatures": [
            {
                "cert_common_name": None,
                "hashed_binary_data": None,
                "hashing_algorithm": None,
                "is_valid": None,
                "is_valid_cert": None,
                "is_valid_hash": None,
                "signers_serial": None,
            }
        ],
    }
