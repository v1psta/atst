from .forms import BaseForm
from wtforms.fields import StringField, TextAreaField, FieldList
from wtforms.validators import Required, Optional
from atst.forms.validators import ListItemRequired, ListItemsUnique
from atst.utils.localization import translate


class EditEnvironmentForm(BaseForm):
    name = StringField(
        label=translate("forms.environments.name_label"),
        validators=[Required()],
        filters=[BaseForm.remove_empty_string],
    )


class NameAndDescriptionForm(BaseForm):
    name = StringField(
        label=translate("forms.application.name_label"),
        validators=[Required()],
        filters=[BaseForm.remove_empty_string],
    )
    description = TextAreaField(
        label=translate("forms.application.description_label"),
        validators=[Optional()],
        filters=[BaseForm.remove_empty_string],
    )


class EnvironmentsForm(BaseForm):
    environment_names = FieldList(
        StringField(
            label=translate("forms.application.environment_names_label"),
            filters=[BaseForm.remove_empty_string],
        ),
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
