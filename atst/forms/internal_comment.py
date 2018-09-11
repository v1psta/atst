from wtforms.fields import TextAreaField
from wtforms.validators import Optional

from .forms import ValidatedForm


class InternalCommentForm(ValidatedForm):
    text = TextAreaField(validators=[Optional()])
