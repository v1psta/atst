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


class Validator:

    _PEM_RE = re.compile(
        b"-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?",
        re.DOTALL,
    )

    def __init__(self, crl_locations=[], roots=[], base_store=crypto.X509Store):
        self.errors = []
        self.crl_locations = crl_locations
        self.roots = roots
        self.base_store = base_store
        self._reset()

    def _reset(self):
        self.cache = {}
        self.store = self.base_store()
        self._add_crls(self.crl_locations)
        self._add_roots(self.roots)
        self.store.set_flags(crypto.X509StoreFlags.CRL_CHECK)

    def _add_crls(self, locations):
        for filename in locations:
            try:
                self._add_crl(filename)
            except crypto.Error as err:
                self.errors.append(
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

    def refresh_cache(self, cert):
        der = cert.get_issuer().der()
        if der in self.cache:
            filename, checksum = self.cache[der]
            if sha256_checksum(filename) != checksum:
                self._reset()

    def validate(self, cert):
        parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        self.refresh_cache(parsed)
        context = crypto.X509StoreContext(self.store, parsed)
        try:
            context.verify_certificate()
            return True

        except crypto.X509StoreContextError as err:
            self.errors.append(
                "Certificate revoked or errored. Error: {}. Args: {}".format(
                    type(err), err.args
                )
            )
            return False
