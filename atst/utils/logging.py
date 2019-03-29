import datetime
import json
import logging


class ContextFilter(logging.Filter):
    # this should impart the request_id and user_id if available
    pass


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
