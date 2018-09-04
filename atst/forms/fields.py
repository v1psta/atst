from wtforms.fields import Field, SelectField as SelectField_
from wtforms.widgets import TextArea


class NewlineListField(Field):
    widget = TextArea()

    def _value(self):
        if isinstance(self.data, list):
            return "\n".join(self.data)
        elif self.data:
            return self.data
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [l.strip() for l in valuelist[0].split("\n") if l]
        else:
            self.data = []

    def process_data(self, value):
        if isinstance(value, list):
            self.data = "\n".join(value)
        else:
            self.data = value


class SelectField(SelectField_):
    def __init__(self, *args, **kwargs):
        render_kw = kwargs.get("render_kw", {})
        kwargs["render_kw"] = {**render_kw, "required": False}
        super().__init__(*args, **kwargs)
