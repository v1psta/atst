from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import Email, Optional

from .forms import ValidatedForm
from .validators import Alphabet, PhoneNumber


class CCPOReviewForm(ValidatedForm):
    comment = TextAreaField(
        "Instructions or comments",
        description="Provide instructions or notes for additional information that is necessary to approve the request here. The requestor may then re-submit the updated request or initiate contact outside of AT-AT if further discussion is required. <strong>This message will be shared with the person making the JEDI request.</strong>.",
    )
    fname_mao = StringField(
        "First Name (optional)", validators=[Optional(), Alphabet()]
    )
    lname_mao = StringField("Last Name (optional)", validators=[Optional(), Alphabet()])
    email_mao = EmailField(
        "Mission Owner e-mail (optional)", validators=[Optional(), Email()]
    )
    phone_mao = TelField(
        "Mission Owner phone number (optional)", validators=[Optional(), PhoneNumber()]
    )
    fname_ccpo = StringField(
        "First Name (optional)", validators=[Optional(), Alphabet()]
    )
    lname_ccpo = StringField(
        "Last Name (optional)", validators=[Optional(), Alphabet()]
    )
