import datetime
import json
import logging

from flask import g, request, has_request_context


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            if getattr(g, "current_user", None):
                record.user_id = str(g.current_user.id)

            if request.environ.get("HTTP_X_REQUEST_ID"):
                record.request_id = request.environ.get("HTTP_X_REQUEST_ID")

        return True


def epoch_to_iso8601(ts):
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.replace(tzinfo=datetime.timezone.utc).isoformat()


class JsonFormatter(logging.Formatter):
    _DEFAULT_RECORD_FIELDS = [
        ("timestamp", lambda r: epoch_to_iso8601(r.created)),
        ("version", lambda r: 1),
        ("request_id", lambda r: r.__dict__.get("request_id")),
        ("user_id", lambda r: r.__dict__.get("user_id")),
        ("severity", lambda r: r.levelname),
        ("tags", lambda r: r.__dict__.get("tags")),
        ("message", lambda r: r.msg),
    ]

    def format(self, record):
        message_dict = {}
        for field, func in self._DEFAULT_RECORD_FIELDS:
            message_dict[field] = func(record)

        if record.__dict__.get("exc_info") is not None:
            message_dict["details"] = {
                "backtrace": self.formatException(record.exc_info),
                "exception": str(record.exc_info[1]),
            }

        return json.dumps(message_dict)
