from flask import template_rendered
from contextlib import contextmanager
from unittest.mock import Mock
from OpenSSL import crypto

from atst.utils.notification_sender import NotificationSender


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class FakeLogger:
    def __init__(self):
        self.messages = []
        self.extras = []

    def log(self, _lvl, msg, *args, **kwargs):
        self._log(_lvl, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log("info", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log("warning", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log("error", msg, *args, **kwargs)

    def _log(self, _lvl, msg, *args, **kwargs):
        self.messages.append(msg)
        if "extra" in kwargs:
            self.extras.append(kwargs["extra"])


FakeNotificationSender = lambda: Mock(spec=NotificationSender)


def parse_for_issuer_and_next_update(crl):
    with open(crl, "rb") as crl_file:
        parsed = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
        next_update = parsed.to_cryptography().next_update
        return (parsed.get_issuer().der(), next_update)
