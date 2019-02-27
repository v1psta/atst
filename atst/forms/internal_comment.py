from wtforms.fields import TextAreaField
from wtforms.validators import InputRequired

from .forms import BaseForm
from atst.utils.localization import translate


class InternalCommentForm(BaseForm):
    text = TextAreaField(
        translate("forms.internal_comment.text_label"),
        default="",
        description=translate("forms.internal_comment.text_description"),
        validators=[InputRequired()],
    )
