from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, StringField, TextAreaField
from wtforms.validators import NumberRange, InputRequired
from .fields import DateField
from .forms import ValidatedForm
from .validators import DateRange
import pendulum


class RequestForm(ValidatedForm):

    # Details of Use: General
    dod_component = StringField(
        "DoD Component",
        description="Identify the DoD component that is requesting access to the JEDI Cloud",
    )

    jedi_usage = StringField(
        "JEDI Usage",
        description="Briefly describe how you are expecting to use the JEDI Cloud",
    )

    # Details of Use: Cloud Readiness
    num_software_systems = IntegerField(
        "Number of Software System",
        description="Estimate the number of software systems that will be supported by this JEDI Cloud access request",
    )

    jedi_migration = RadioField(
        "Are you using the JEDI Cloud to migrate existing systems?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    rationalization_software_systems = RadioField(
        "Have you completed a “rationalization” of your software systems to move to the cloud?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress","In Progress")],
    )

    technical_support_team = RadioField(
        "Are you working with a technical support team experienced in cloud migrations?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    organization_providing_assistance = RadioField(
        "If you are receiving migration assistance, indicate the type of organization providing assistance below:",
        choices=[("yes", "Yes"), ("no", "No")],
    )



    # Organization Providing Assistance

    # # Engineering Assessment

    # # Data Transfers

    # # Expected Completion Date

    # # Cloud Native


