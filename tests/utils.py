from flask import template_rendered
from contextlib import contextmanager


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

    def log(self, _lvl, msg, *args, **kwargs):
        self.messages.append(msg)

    def info(self, msg, *args, **kwargs):
        self.messages.append(msg)

    def warning(self, msg, *args, **kwargs):
        self.messages.append(msg)

    def error(self, msg, *args, **kwargs):
        self.messages.append(msg)
