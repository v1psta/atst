import pendulum
from wtforms.fields.html5 import DateField, EmailField, TelField
from wtforms.fields import RadioField, StringField
from wtforms.validators import Email, Required

from .fields import SelectField
from .forms import ValidatedForm
from .data import (
    SERVICE_BRANCHES,
)

from .validators import Alphabet, DateRange, PhoneNumber


class EditUserForm(ValidatedForm):

    fname = StringField("First Name", validators=[Required(), Alphabet()])

    lname = StringField("Last Name", validators=[Required(), Alphabet()])

    email = EmailField("E-mail Address", validators=[Required(), Email()])

    phone_number = TelField(
        "Phone Number",
        description="Enter a 10-digit phone number",
        validators=[Required(), PhoneNumber()],
    )

    service_branch = SelectField(
        "Service Branch or Agency",
        description="Which service or organization do you belong to within the DoD?",
        choices=SERVICE_BRANCHES,
    )

    citizenship = RadioField(
        description="What is your citizenship status?",
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
        validators=[Required()],
    )

    designation = RadioField(
        "Designation of Person",
        description="What is your designation within the DoD?",
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
        validators=[Required()],
    )

    date_latest_training = DateField(
        "Latest Information Assurance (IA) Training Completion Date",
        description='To complete the training, you can find it in <a class="icon-link" href="https://iatraining.disa.mil/eta/disa_cac2018/launchPage.htm" target="_blank">Information Assurance Cyber Awareness Challange</a> website.',
        validators=[
            Required(),
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            ),
        ],
        format="%m/%d/%Y",
    )
