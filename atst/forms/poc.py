from wtforms.fields import StringField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length, Optional
from .forms import ValidatedForm
from .validators import IsNumber


class POCForm(ValidatedForm):

    def validate(self, *args, **kwargs):
        if self.am_poc.data == "yes":
            self.fname_poc.validators.insert(0, Optional())
            self.lname_poc.validators.insert(0, Optional())
            self.email_poc.validators.insert(0, Optional())
            self.dodid_poc.validators.insert(0, Optional())

        return super(POCForm, self).validate(*args, **kwargs)


    am_poc = RadioField(
        "I am the technical POC.",
        choices=[("yes", "Yes"), ("no", "No")],
        default="no",
        validators=[Required()],
    )

    fname_poc = StringField("POC First Name", validators=[Required()])

    lname_poc = StringField("POC Last Name", validators=[Required()])

    email_poc = EmailField("POC Email Address", validators=[Required(), Email()])

    dodid_poc = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )
