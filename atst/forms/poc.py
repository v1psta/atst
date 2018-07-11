from wtforms.fields import StringField
from wtforms.validators import Required, Email, Length
from .forms import ValidatedForm
from .validators import IsNumber, Alphabet


class POCForm(ValidatedForm):
    fname_poc = StringField("POC First Name", validators=[Required(), Alphabet()])
    lname_poc = StringField("POC Last Name", validators=[Required(), Alphabet()])

    email_poc = StringField("POC Email Address", validators=[Required(), Email()])

    dodid_poc = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )
