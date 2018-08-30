import re
import json
from flask import current_app as app
from werkzeug.datastructures import FileStorage


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
        and isinstance(value["task_order"], FileStorage)
    ):
        value["task_order"] = value["task_order"].filename
    return app.jinja_env.filters["tojson"](value)

def toJson(data):
    return json.dumps(data)

def register_filters(app):
    app.jinja_env.filters["iconSvg"] = iconSvg
    app.jinja_env.filters["dollars"] = dollars
    app.jinja_env.filters["usPhone"] = usPhone
    app.jinja_env.filters["readableInteger"] = readableInteger
    app.jinja_env.filters["getOptionLabel"] = getOptionLabel
    app.jinja_env.filters["mixedContentToJson"] = mixedContentToJson
    app.jinja_env.filters["toJson"] = toJson
