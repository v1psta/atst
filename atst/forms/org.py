from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Required, Length, Email
from wtforms_tornado import Form
import pendulum
from .fields import DateField
from .validators import DateRange


class OrgForm(Form):
    fname_request = StringField("First Name", validators=[Required()])
    lname_request = StringField("Last Name", validators=[Required()])

    email_request = EmailField("Email Address", validators=[Required(), Email()])
    )

    phone_number = TelField("Phone Number", validators=[Required(), Length(min=7)])

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
        "Latest Information Assurance (IA) Training completion date.",
        validators=[
            Required(),
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            ),
        ],
    )
