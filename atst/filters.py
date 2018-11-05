import re
import datetime
from flask import current_app as app
from werkzeug.datastructures import FileStorage
from atst.models.attachment import Attachment


def iconSvg(name):
    with open("static/icons/" + name + ".svg") as contents:
        return contents.read()


def dollars(value):
    try:
        numberValue = float(value)
    except ValueError:
        numberValue = 0
    return "${:,.0f}".format(numberValue)


def usPhone(number):
    phone = re.sub(r"\D", "", number)
    return "+1 ({}) {} - {}".format(phone[0:3], phone[3:6], phone[6:])


def readableInteger(value):
    try:
        numberValue = int(value)
    except ValueError:
        numberValue = 0
    return "{:,}".format(numberValue)


def getOptionLabel(value, options):
    if hasattr(value, "value"):
        value = value.name
    try:
        return next(tup[1] for tup in options if tup[0] == value)
    except StopIteration:
        return


def mixedContentToJson(value):
    """
    This coerces the file upload in form data to its filename
    so that the data can be JSON serialized.
    """
    if (
        isinstance(value, dict)
        and "task_order" in value
        and (
            isinstance(value["task_order"]["pdf"], FileStorage)
            or isinstance(value["task_order"]["pdf"], Attachment)
        )
    ):
        value["task_order"]["pdf"] = value["task_order"]["pdf"].filename
    return app.jinja_env.filters["tojson"](value)


def findFilter(value, filter_name, filter_args=[]):
    if not filter_name:
        return value
    elif filter_name in app.jinja_env.filters:
        return app.jinja_env.filters[filter_name](value, *filter_args)
    else:
        raise ValueError("filter name {} not found".format(filter_name))


def renderList(value):
    return app.jinja_env.filters["safe"]("<br>".join(value))


def formattedDate(value, formatter="%m/%d/%Y"):
    if value:
        return value.strftime(formatter)
    else:
        return "-"


def dateFromString(value, formatter="%m/%Y"):
    return datetime.datetime.strptime(value, formatter)


def register_filters(app):
    app.jinja_env.filters["iconSvg"] = iconSvg
    app.jinja_env.filters["dollars"] = dollars
    app.jinja_env.filters["usPhone"] = usPhone
    app.jinja_env.filters["readableInteger"] = readableInteger
    app.jinja_env.filters["getOptionLabel"] = getOptionLabel
    app.jinja_env.filters["mixedContentToJson"] = mixedContentToJson
    app.jinja_env.filters["findFilter"] = findFilter
    app.jinja_env.filters["renderList"] = renderList
    app.jinja_env.filters["formattedDate"] = formattedDate
    app.jinja_env.filters["dateFromString"] = dateFromString
