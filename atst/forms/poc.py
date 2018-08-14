from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length
from .forms import ValidatedForm
from .validators import IsNumber


class POCForm(ValidatedForm):
    fname_poc = StringField("First Name", validators=[Required()])

    lname_poc = StringField("Last Name", validators=[Required()])

    email_poc = EmailField("Email Address", validators=[Required(), Email()])

    dodid_poc = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )
