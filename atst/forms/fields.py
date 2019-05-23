from wtforms.fields import FormField, SelectField as SelectField_, HiddenField
from atst.utils.encryption import encrypt_value, decrypt_value


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


class EncryptedHiddenField(HiddenField):
    def process_data(self, value):
        self.data = encrypt_value(value)

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = decrypt_value(valuelist[0])
            except ValueError:
                raise ValueError(self.gettext("Invalid Choice: could not coerce"))
