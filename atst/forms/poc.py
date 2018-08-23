from wtforms.fields import StringField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length, Optional
from .forms import ValidatedForm
from .validators import IsNumber


class POCForm(ValidatedForm):
    def validate(self, *args, **kwargs):
        if self.am_poc.data:
            # Prepend Optional validators so that the validation chain
            # halts if no data exists.
            self.fname_poc.validators.insert(0, Optional())
            self.lname_poc.validators.insert(0, Optional())
            self.email_poc.validators.insert(0, Optional())
            self.dodid_poc.validators.insert(0, Optional())

        return super().validate(*args, **kwargs)

    am_poc = BooleanField(
        "I am the Workspace Owner",
        default=False,
        false_values=(False, "false", "False", "no", ""),
    )

    fname_poc = StringField("First Name", validators=[Required()])

    lname_poc = StringField("Last Name", validators=[Required()])

    email_poc = EmailField("Email Address", validators=[Required(), Email()])

    dodid_poc = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )
