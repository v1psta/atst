from wtforms.fields import TextAreaField
from wtforms.validators import InputRequired

from .forms import CacheableForm
from atst.utils.localization import translate


class InternalCommentForm(CacheableForm):
    text = TextAreaField(
        translate("forms.internal_comment.text_label"),
        default="",
        description=translate("forms.internal_comment.text_description"),
        validators=[InputRequired()],
    )
