from wtforms.fields import StringField
from wtforms.validators import Length

from .forms import CacheableForm
from atst.utils.localization import translate


class WorkspaceForm(CacheableForm):
    name = StringField(
        translate("forms.workspace.name_label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.workspace.name_length_validation_message"),
            )
        ],
    )
