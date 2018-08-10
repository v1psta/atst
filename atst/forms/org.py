from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Required, Email
import pendulum
from .fields import DateField
from .forms import ValidatedForm
from .validators import DateRange, PhoneNumber, Alphabet


class OrgForm(ValidatedForm):
    fname_request = StringField("First Name", validators=[Required(), Alphabet()])

    lname_request = StringField("Last Name", validators=[Required(), Alphabet()])

    email_request = EmailField("E-mail Address", validators=[Required(), Email()])

    phone_number = TelField("Phone Number",
        description='Enter a 10-digit phone number',
        validators=[Required(), PhoneNumber()])

    service_branch = StringField("Service Branch or Agency", validators=[Required()])

    citizenship = RadioField(
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
        validators=[Required()],
    )

    designation = RadioField(
        "Designation of Person",
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
        validators=[Required()],
    )

    date_latest_training = DateField(
        "Latest Information Assurance (IA) Training completion date",
        validators=[
            Required(),
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            ),
        ],
    )
