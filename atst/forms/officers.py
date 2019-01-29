from flask_wtf import FlaskForm
from wtforms.fields import FormField, StringField
from wtforms.fields.html5 import TelField
from wtforms.validators import Length, Optional

from atst.forms.validators import IsNumber, PhoneNumber

from .forms import CacheableForm


class OfficerForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("Email")
    phone_number = TelField("Phone Number", validators=[PhoneNumber()])
    dod_id = StringField("DoD ID", validators=[Optional(), Length(min=10), IsNumber()])


class EditTaskOrderOfficersForm(CacheableForm):

    contracting_officer = FormField(OfficerForm)
    contracting_officer_representative = FormField(OfficerForm)
    security_officer = FormField(OfficerForm)

    OFFICER_PREFIXES = {
        "contracting_officer": "ko",
        "contracting_officer_representative": "cor",
        "security_officer": "so",
    }
    OFFICER_INFO_FIELD_NAMES = [
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "dod_id",
    ]

    def process(self, formdata=None, obj=None, data=None, **kwargs):
        if obj:
            for name, field in self._fields.items():
                if name in self.OFFICER_PREFIXES:
                    prefix = self.OFFICER_PREFIXES[name]
                    officer_data = {
                        field_name: getattr(obj, prefix + "_" + field_name)
                        for field_name in self.OFFICER_INFO_FIELD_NAMES
                    }
                    field.process(formdata=formdata, data=officer_data)
                else:
                    field.process(formdata)
        else:
            super(EditTaskOrderOfficersForm, self).process(
                formdata=formdata, obj=obj, data=data, **kwargs
            )

    def populate_obj(self, obj):
        for name, field in self._fields.items():
            if name in self.OFFICER_PREFIXES:
                prefix = self.OFFICER_PREFIXES[name]
                for field_name in self.OFFICER_INFO_FIELD_NAMES:
                    setattr(obj, prefix + "_" + field_name, field[field_name].data)
