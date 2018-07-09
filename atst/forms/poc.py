from wtforms.fields import StringField
from wtforms.validators import Required, Email, Length
from wtforms_tornado import Form
from .validators import IsNumber


class POCForm(Form):
    fname_poc = StringField("POC First Name", validators=[Required()])
    lname_poc = StringField("POC Last Name", validators=[Required()])

    email_poc = StringField(
        "POC Email Address", validators=[Required(), Email()]
    )

    dodid_poc = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )
