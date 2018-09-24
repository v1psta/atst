from wtforms.fields import TextAreaField
from wtforms.validators import Optional

from .forms import ValidatedForm


class InternalCommentForm(ValidatedForm):
    text = TextAreaField(
        "CCPO Internal Notes",
        description="Add comments or notes for internal CCPO reference and follow-up here.<strong>These comments <em>will not</em> be visible to the person making the JEDI request.</strong>",
        validators=[Optional()],
    )
