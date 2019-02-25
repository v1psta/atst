import sys
import os
import re
import hashlib
from OpenSSL import crypto, SSL


def get_common_name(x509_name_object):
    for comp in x509_name_object.get_components():
        if comp[0] == b"CN":
            return comp[1].decode()


class CRLRevocationException(Exception):
    pass


class CRLInterface:
    def __init__(self, *args, logger=None, **kwargs):
        self.logger = logger

    def _log_info(self, message):
        if self.logger:
            self.logger.info(message)

    def crl_check(self, cert):
        raise NotImplementedError()


class NoOpCRLCache(CRLInterface):
    def _get_cn(self, cert):
        try:
            parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
            return get_common_name(parsed.get_subject())
        except crypto.Error:
            pass

        return "unknown"

    def crl_check(self, cert):
        cn = self._get_cn(cert)
        self._log_info(
            "Did not perform CRL validation for certificate with Common Name '{}'".format(
                cn
            )
        )

        return True


class CRLCache(CRLInterface):

    _PEM_RE = re.compile(
        b"-----BEGIN CERTIFICATE-----\r?.+?\r?-----END CERTIFICATE-----\r?\n?",
        re.DOTALL,
    )

    def __init__(
        self, root_location, crl_locations=[], store_class=crypto.X509Store, logger=None
    ):
        self.logger = logger
        self.store_class = store_class
        self.certificate_authorities = {}
        self._load_roots(root_location)
        self._build_crl_cache(crl_locations)

    def _get_store(self, cert):
        return self._build_store(cert.get_issuer())

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
            if crl:
                issuer_der = crl.get_issuer().der()
                expires = crl.to_cryptography().next_update
                self.crl_cache[issuer_der] = {
                    "location": crl_location,
                    "expires": expires,
                }

    def _load_crl(self, crl_location):
        with open(crl_location, "rb") as crl_file:
            try:
                return crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
            except crypto.Error:
                self._log_info("Could not load CRL at location {}".format(crl_location))

    def _build_store(self, issuer):
        store = self.store_class()
        self._log_info("STORE ID: {}. Building store.".format(id(store)))
        store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
        crl_info = self.crl_cache.get(issuer.der(), {})
        issuer_name = get_common_name(issuer)

        if not crl_info:
            raise CRLRevocationException(
                "Could not find matching CRL for issuer with Common Name {}".format(
                    issuer_name
                )
            )

        crl = self._load_crl(crl_info["location"])
        store.add_crl(crl)

        self._log_info(
            "STORE ID: {}. Adding CRL with issuer Common Name {}".format(
                id(store), issuer_name
            )
        )

        store = self._add_certificate_chain_to_store(store, crl.get_issuer())
        return store

    # this _should_ happen just twice for the DoD PKI (intermediary, root) but
    # theoretically it can build a longer certificate chain

    def _add_certificate_chain_to_store(self, store, issuer):
        ca = self.certificate_authorities.get(issuer.der())
        store.add_cert(ca)
        self._log_info(
            "STORE ID: {}. Adding CA with subject {}".format(
                id(store), ca.get_subject()
            )
        )

        if issuer == ca.get_issuer():
            # i.e., it is the root CA and we are at the end of the chain
            return store

        else:
            return self._add_certificate_chain_to_store(store, ca.get_issuer())

    def crl_check(self, cert):
        parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        store = self._get_store(parsed)
        context = crypto.X509StoreContext(store, parsed)
        try:
            context.verify_certificate()
            return True

        except crypto.X509StoreContextError as err:
            raise CRLRevocationException(
                "Certificate revoked or errored. Error: {}. Args: {}".format(
                    type(err), err.args
                )
            )
