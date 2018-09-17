from wtforms.fields import TextAreaField
from wtforms.validators import Optional

from .forms import ValidatedForm


class InternalCommentForm(ValidatedForm):
    text = TextAreaField(
        "CCPO Internal Notes",
        description="You may add additional comments and notes for internal CCPO reference and follow-up here.",
        validators=[Optional()],
    )
