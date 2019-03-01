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
