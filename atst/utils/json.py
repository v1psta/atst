from flask.json import JSONEncoder
from datetime import date
from atst.models.attachment import Attachment


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Attachment):
            return obj.filename
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        return JSONEncoder.default(self, obj)
