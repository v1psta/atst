from wtforms.fields.html5 import IntegerField
from wtforms.fields import RadioField, StringField, TextAreaField, SelectField
from wtforms.validators import NumberRange, InputRequired
from .fields import DateField
from .forms import ValidatedForm
from .validators import DateRange
import pendulum


class RequestForm(ValidatedForm):

    # Details of Use: General
    dod_component = SelectField(
        "DoD Component",
        description="Identify the DoD component that is requesting access to the JEDI Cloud",
        choices=[
          ("null","Select an option"),
          ("us_air_force","US Air Force"),
          ("us_army","US Army"),
          ("us_navy","US Navy"),
          ("us_marine_corps","US Marine Corps"),
          ("joint_chiefs_of_staff","Joint Chiefs of Staff")],
    )

    jedi_usage = TextAreaField(
        "JEDI Usage",
        description="Briefly describe how you are expecting to use the JEDI Cloud",
        render_kw={"placeholder": "e.g. We are migrating XYZ application to the cloud so that..."},
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

    engineering_assessment = RadioField(
        description="Have you completed an engineering assessment of your software systems for cloud readiness?",
        choices=[("yes", "Yes"), ("no", "No"), ("in_progress","In Progress")],
    )

    data_transfers = StringField(
        "How much data is being transferred to the cloud?",
    )

    expected_completion_date = StringField(
        "When do you expect to complete your migration to the JEDI Cloud?",
    )

    cloud_native = RadioField(
        "Are your software systems being developed cloud native?",
        choices=[("yes", "Yes"), ("no", "No")],
    )

    # Details of Use: Financial Usage
    estimated_monthly_spend = IntegerField(
        "Estimated monthly spend",
        description="Use the <a href=\"#\">JEDI CSP Calculator</a> to estimate your monthly cloud resource usage and enter the dollar amount below. Note these estimates are for initial approval only. After the request is approved, you will be asked to provide a valid Task Order number with specific CLIN amounts for cloud services."
    )

    total_spend = IntegerField(
        "What is your total expected budget for this JEDI Cloud Request?",
    )

    number_user_sessions = IntegerField(
        "How many user sessions do you expect on these systems each day?",
    )

    average_daily_traffic = IntegerField(
        "What is the average daily traffic you expect the systems under this cloud contract to use?",
    )

    start_date = StringField(
        "When do you expect to start using the JEDI Cloud (not for billing purposes)?",
    )




