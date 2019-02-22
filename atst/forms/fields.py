from wtforms.fields import FormField, SelectField as SelectField_


class SelectField(SelectField_):
    def __init__(self, *args, **kwargs):
        render_kw = kwargs.get("render_kw", {})
        kwargs["render_kw"] = {**render_kw, "required": False}
        super().__init__(*args, **kwargs)


class FormFieldWrapper(FormField):
    def has_changes(self):
        if not self.object_data:
            return False

        for (attr, field) in self._fields.items():
            if attr in self.object_data and self.object_data[attr] != field.data:
                return True
        return False
