from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, FieldList
from wtforms.validators import Required
from atst.forms.validators import ListItemRequired, ListItemsUnique
from atst.utils.localization import translate


class ApplicationForm(FlaskForm):
    name = StringField(
        label=translate("forms.application.name_label"), validators=[Required()]
    )
    description = TextAreaField(
        label=translate("forms.application.description_label"), validators=[Required()]
    )


class NewApplicationForm(ApplicationForm):
    EMPTY_ENVIRONMENT_NAMES = ["", None]

    environment_names = FieldList(
        StringField(label=translate("forms.application.environment_names_label")),
        validators=[
            ListItemRequired(
                message=translate(
                    "forms.application.environment_names_required_validation_message"
                )
            ),
            ListItemsUnique(
                message=translate(
                    "forms.application.environment_names_unique_validation_message"
                )
            ),
        ],
    )

    @property
    def data(self):
        _data = super(FlaskForm, self).data
        _data["environment_names"] = [
            n
            for n in _data["environment_names"]
            if n not in self.EMPTY_ENVIRONMENT_NAMES
        ]
        return _data
