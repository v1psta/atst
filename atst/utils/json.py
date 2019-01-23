from flask.json import JSONEncoder
from atst.models.attachment import Attachment


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Attachment):
            return obj.filename
        return JSONEncoder.default(self, obj)
