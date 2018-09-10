from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import Email

from .forms import ValidatedForm
from .validators import Alphabet, PhoneNumber


class CCPOReviewForm(ValidatedForm):
    comment = TextAreaField("Comments (optional)")
    fname_mao = StringField("First Name (optional)", validators=[Alphabet()])
    lname_mao = StringField("Last Name (optional)", validators=[Alphabet()])
    email_mao = EmailField("Mission Owner e-mail (optional)", validators=[Email()])
    phone_mao = TelField(
        "Mission Owner phone number (optional)", validators=[PhoneNumber()]
    )
    fname_ccpo = StringField("First Name (optional)", validators=[Alphabet()])
    lname_ccpo = StringField("Last Name (optional)", validators=[Alphabet()])
