from wtforms.fields import Field, FormField, StringField, SelectField as SelectField_
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


class NumberStringField(StringField):
    def process_data(self, value):
        if isinstance(value, int):
            self.data = str(value)
        else:
            self.data = value


class FormFieldWrapper(FormField):
    def has_changes(self):
        if not self.object_data:
            return False

        for (attr, field) in self._fields.items():
            if attr in self.object_data and self.object_data[attr] != field.data:
                return True
        return False
