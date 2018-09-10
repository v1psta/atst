from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import Required, Email

from .forms import ValidatedForm
from .validators import Alphabet, PhoneNumber


class CCPOReviewForm(ValidatedForm):
    comments = TextAreaField(
        "Comments",
        description="Add notes or comments explaining what changes are being requested or why further discussion is needed about this request.",
    )
    fname_mao = StringField("First Name", validators=[Required(), Alphabet()])
    lname_mao = StringField("Last Name", validators=[Required(), Alphabet()])
    email_mao = EmailField("Mission Owner e-mail (optional)", validators=[Email()])
    phone_mao = TelField(
        "Mission Owner phone number (optional)",
        validators=[Required(), PhoneNumber()],
    )
    fname_ccpo = StringField("First Name", validators=[Required(), Alphabet()])
    lname_ccpo = StringField("Last Name", validators=[Required(), Alphabet()])
