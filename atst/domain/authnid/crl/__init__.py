import sys
import os
import re
import hashlib
from OpenSSL import crypto, SSL


class CRLException(Exception):
    pass


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()


def crl_check(cache, cert):
    parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    store = cache.get_store(parsed)
    context = crypto.X509StoreContext(store, parsed)
    try:
        context.verify_certificate()
        return True

    except crypto.X509StoreContextError as err:
        raise CRLException(
            "Certificate revoked or errored. Error: {}. Args: {}".format(
                type(err), err.args
            )
        )


class CRLCache():

    _PEM_RE = re.compile(
        b"-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?",
        re.DOTALL,
    )

    def __init__(self, root_location, crl_locations=[], store_class=crypto.X509Store):
        self.store_class = store_class
        self.certificate_authorities = {}
        self._load_roots(root_location)
        self._build_crl_cache(crl_locations)

    def get_store(self, cert):
        return self._build_store(cert.get_issuer().der())

    def _load_roots(self, root_location):
        with open(root_location, "rb") as f:
            for raw_ca in self._parse_roots(f.read()):
                ca = crypto.load_certificate(crypto.FILETYPE_PEM, raw_ca)
                self.certificate_authorities[ca.get_subject().der()] = ca

    def _parse_roots(self, root_str):
        return [match.group(0) for match in self._PEM_RE.finditer(root_str)]

    def _build_crl_cache(self, crl_locations):
        self.crl_cache = {}
        for crl_location in crl_locations:
            crl = self._load_crl(crl_location)
            self.crl_cache[crl.get_issuer().der()] = crl_location

    def _load_crl(self, crl_location):
        with open(crl_location, "rb") as crl_file:
            return crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())

    def _build_store(self, issuer):
        store = self.store_class()
        store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
        crl_location = self.crl_cache[issuer]
        with open(crl_location, "rb") as crl_file:
            crl = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
            store.add_crl(crl)
            store = self._add_certificate_chain_to_store(store, crl.get_issuer())
            return store

    # this _should_ happen just twice for the DoD PKI (intermediary, root) but
    # theoretically it can build a longer certificate chain
    def _add_certificate_chain_to_store(self, store, issuer):
        ca = self.certificate_authorities.get(issuer.der())
        store.add_cert(ca)

        if issuer == ca.get_subject():
            # i.e., it is the root CA and we are at the end of the chain
            return store
        else:
            return self._add_certificate_chain_to_store(store, ca.get_issuer())

