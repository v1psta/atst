from wtforms.fields.html5 import DateField
from wtforms.fields import Field
from wtforms.widgets import TextArea

from atst.domain.date import parse_date


class DateField(DateField):
    def _value(self):
        if self.data:
            return parse_date(self.data)
        else:
            return None

    def process_formdata(self, values):
        if values:
            self.data = values[0]
        else:
            self.data = []


class NewlineListField(Field):
    widget = TextArea()

    def _value(self):
        if isinstance(self.data, list):
            return '\n'.join(self.data)
        elif self.data:
            return self.data
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [l.strip() for l in valuelist[0].split("\n")]
        else:
            self.data = []
