import sys
import os
import re
import hashlib
from OpenSSL import crypto, SSL


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    return sha256.hexdigest()


class CRLCache():

    _PEM_RE = re.compile(
        b"-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?",
        re.DOTALL,
    )

    def __init__(self, root_location, crl_locations=[], store_class=crypto.X509Store):
        self.crl_cache = {}
        self.store_class = store_class
        self._load_roots(root_location)
        self._build_x509_stores(crl_locations)

    def _load_roots(self, root_location):
        self.certificate_authorities = {}
        with open(root_location, "rb") as f:
            for raw_ca in self._parse_roots(f.read()):
                ca = crypto.load_certificate(crypto.FILETYPE_PEM, raw_ca)
                self.certificate_authorities[ca.get_subject().der()] = ca

    def _parse_roots(self, root_str):
        return [match.group(0) for match in self._PEM_RE.finditer(root_str)]

    def _build_x509_stores(self, crl_locations):
        self.x509_stores = {}
        for crl_path in crl_locations:
            issuer, store = self._build_store(crl_path)
            self.x509_stores[issuer] = store

    def _build_store(self, crl_location):
        store = self.store_class()
        store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
        with open(crl_location, "rb") as crl_file:
            crl = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
            self.crl_cache[crl.get_issuer().der()] = (crl_location, sha256_checksum(crl_location))
            store.add_crl(crl)
            store = self._add_certificate_chain_to_store(store, crl.get_issuer())
            return (crl.get_issuer().der(), store)

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

    def get_store(self, cert):
        return self._check_cache(cert.get_issuer().der())

    def _check_cache(self, issuer):
        if issuer in self.crl_cache:
            filename, checksum = self.crl_cache[issuer]
            if sha256_checksum(filename) != checksum:
                issuer, store = self._build_store(filename)
                self.x509_stores[issuer] = store
                return store
            else:
                return self.x509_stores[issuer]


class Validator:

    def __init__(self, cache, cert, logger=None):
        self.cache = cache
        self.cert = cert
        self.logger = logger

    def validate(self):
        parsed = crypto.load_certificate(crypto.FILETYPE_PEM, self.cert)
        store = self.cache.get_store(parsed)
        context = crypto.X509StoreContext(store, parsed)
        try:
            context.verify_certificate()
            return True

        except crypto.X509StoreContextError as err:
            self.log_error(
                "Certificate revoked or errored. Error: {}. Args: {}".format(
                    type(err), err.args
                )
            )
            return False

    def _add_roots(self, roots):
        with open(filename, "rb") as f:
            for raw_ca in self._parse_roots(f.read()):
                ca = crypto.load_certificate(crypto.FILETYPE_PEM, raw_ca)
                self._add_carefully("add_cert", ca)

    def _reset(self):
        self.cache = {}
        self.store = self.base_store()
        self._add_crls(self.crl_locations)
        self._add_roots(self.roots)
        self.store.set_flags(crypto.X509StoreFlags.CRL_CHECK)

    def log_error(self, message):
        if self.logger:
            self.logger.error(message)

    def _add_crls(self, locations):
        for filename in locations:
            try:
                self._add_crl(filename)
            except crypto.Error as err:
                self.log_error(
                    "CRL could not be parsed. Filename: {}, Error: {}, args: {}".format(
                        filename, type(err), err.args
                    )
                )

    # This caches the CRL issuer with the CRL filepath and a checksum, in addition to adding the CRL to the store.

    def _add_crl(self, filename):
        with open(filename, "rb") as crl_file:
            crl = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
            self.cache[crl.get_issuer().der()] = (filename, sha256_checksum(filename))
            self._add_carefully("add_crl", crl)

    def _parse_roots(self, root_str):
        return [match.group(0) for match in self._PEM_RE.finditer(root_str)]

    def _add_roots(self, roots):
        for filename in roots:
            with open(filename, "rb") as f:
                for raw_ca in self._parse_roots(f.read()):
                    ca = crypto.load_certificate(crypto.FILETYPE_PEM, raw_ca)
                    self._add_carefully("add_cert", ca)

    # in testing, it seems that openssl is maintaining a local cache of certs
    # in a hash table and throws errors if you try to add redundant certs or
    # CRLs. For now, we catch and ignore that error with great specificity.

    def _add_carefully(self, method_name, obj):
        try:
            getattr(self.store, method_name)(obj)
        except crypto.Error as error:
            if self._is_preloaded_error(error):
                pass
            else:
                raise error

    PRELOADED_CRL = (
        [
            (
                "x509 certificate routines",
                "X509_STORE_add_crl",
                "cert already in hash table",
            )
        ],
    )
    PRELOADED_CERT = (
        [
            (
                "x509 certificate routines",
                "X509_STORE_add_cert",
                "cert already in hash table",
            )
        ],
    )

    def _is_preloaded_error(self, error):
        return error.args == self.PRELOADED_CRL or error.args == self.PRELOADED_CERT

    # Checks that the CRL currently in-memory is up-to-date via the checksum.
