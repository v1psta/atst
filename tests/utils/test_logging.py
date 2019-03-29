from io import StringIO
import json
import logging

import pytest

from atst.utils.logging import JsonFormatter


@pytest.fixture
def log_stream():
    return StringIO()


@pytest.fixture
def log_stream_content(log_stream):
    def _log_stream_content():
        log_stream.seek(0)
        return log_stream.read()

    return _log_stream_content


@pytest.fixture
def logger(log_stream):
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logHandler = logging.StreamHandler(log_stream)
    formatter = JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    return logger


def test_json_formatter(logger, log_stream_content):
    logger.warning("do or do not", extra={"tags": ["wisdom", "jedi"]})

    log = json.loads(log_stream_content())

    assert log["tags"] == ["wisdom", "jedi"]
    assert log["message"] == "do or do not"
    assert log["severity"] == "WARNING"
    assert log.get("details") is None


def test_json_formatter_for_exceptions(logger, log_stream_content):
    try:
        raise Exception()
    except Exception:
        logger.exception("you found the ventilation shaft!")

    log = json.loads(log_stream_content())
    assert log["severity"] == "ERROR"
    assert log.get("details")
