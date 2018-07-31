from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length
from .forms import ValidatedForm
from .validators import IsNumber, Alphabet


class POCForm(ValidatedForm):
    fname_poc = StringField(
      "POC First Name",
      validators=[Required()]
    )

    lname_poc = StringField(
      "POC Last Name",
      validators=[Required()]
    )

    email_poc = EmailField(
      "POC Email Address",
      validators=[Required(), Email()]
    )

    dodid_poc = StringField(
        "DOD ID",
        validators=[Required(), Length(min=10), IsNumber()]
    )
