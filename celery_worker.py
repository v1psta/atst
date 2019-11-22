#!/usr/bin/env python
import logging

from atst.app import celery, make_app, make_config
from celery.signals import after_setup_task_logger

from atst.utils.logging import JsonFormatter

config = make_config()
app = make_app(config)
app.app_context().push()


@after_setup_task_logger.connect
def setup_task_logger(*args, **kwargs):
    if app.config.get("LOG_JSON"):
        logger = logging.getLogger()
        for handler in logger.handlers:
            handler.setFormatter(JsonFormatter(source="queue"))
