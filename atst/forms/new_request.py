import pendulum
from wtforms.fields.html5 import DateField, EmailField, IntegerField
from wtforms.fields import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import Email, Length, Optional, InputRequired, DataRequired

from .fields import SelectField
from .forms import ValidatedForm
from .edit_user import USER_FIELDS, inherit_field
from .data import (
    SERVICE_BRANCHES,
    ASSISTANCE_ORG_TYPES,
    DATA_TRANSFER_AMOUNTS,
    COMPLETION_DATE_RANGES,
)
from .validators import DateRange, IsNumber
from atst.domain.requests import Requests


class DetailsOfUseForm(ValidatedForm):
    def validate(self, *args, **kwargs):
        if self.jedi_migration.data == "no":
            self.rationalization_software_systems.validators.append(Optional())
            self.technical_support_team.validators.append(Optional())
            self.organization_providing_assistance.validators.append(Optional())
            self.engineering_assessment.validators.append(Optional())
            self.data_transfers.validators.append(Optional())
            self.expected_completion_date.validators.append(Optional())
        elif self.jedi_migration.data == "yes":
            if self.technical_support_team.data == "no":
                self.organization_providing_assistance.validators.append(Optional())
            self.cloud_native.validators.append(Optional())

        try:
            annual_spend = int(self.estimated_monthly_spend.data or 0) * 12
        except ValueError:
            annual_spend = 0

        if annual_spend > Requests.AUTO_APPROVE_THRESHOLD:
            self.number_user_sessions.validators.append(InputRequired())
            self.average_daily_traffic.validators.append(InputRequired())

        return super(DetailsOfUseForm, self).validate(*args, **kwargs)

    # Details of Use: General
    dod_component = SelectField(
        "DoD Component",
        description="Identify the DoD component that is requesting access to the JEDI Cloud",
        choices=SERVICE_BRANCHES,
        validators=[InputRequired()],
    )

    jedi_usage = TextAreaField(
        "JEDI Usage",
        description="Your answer will help us provide tangible examples to DoD leadership how and why commercial cloud resources are accelerating the Department's missions",
        validators=[InputRequired()],
    )

    # Details of Use: Cloud Readiness
    num_software_systems = IntegerField(
        "Number of Software Systems",
        description="Estimate the number of software systems that will be supported by this JEDI Cloud access request",
    )

    jedi_migration = RadioField(
        "JEDI Migration",
        description="Are you using the JEDI Cloud to migrate existing systems?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    rationalization_software_systems = RadioField(
        description="Have you completed a “rationalization” of your software systems to move to the cloud?",
        choices=[("yes", "Yes"), ("no", "No"), ("In Progress", "In Progress")],
        default="",
    )

    technical_support_team = RadioField(
        description="Are you working with a technical support team experienced in cloud migrations?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    organization_providing_assistance = RadioField(  # this needs to be updated to use checkboxes instead of radio
        description="If you are receiving migration assistance, what is the type of organization providing assistance?",
        choices=ASSISTANCE_ORG_TYPES,
        default="",
    )

    engineering_assessment = RadioField(
        description="Have you completed an engineering assessment of your systems for cloud readiness?",
        choices=[("yes", "Yes"), ("no", "No"), ("In Progress", "In Progress")],
        default="",
    )

    data_transfers = SelectField(
        description="How much data is being transferred to the cloud?",
        choices=DATA_TRANSFER_AMOUNTS,
        validators=[DataRequired()],
    )

    expected_completion_date = SelectField(
        description="When do you expect to complete your migration to the JEDI Cloud?",
        choices=COMPLETION_DATE_RANGES,
        validators=[DataRequired()],
    )

    cloud_native = RadioField(
        description="Are your software systems being developed cloud native?",
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    # Details of Use: Financial Usage
    estimated_monthly_spend = IntegerField(
        "Estimated Monthly Spend",
        description='Use the <a href="#" target="_blank" class="icon-link">JEDI CSP Calculator</a> to estimate your <b>monthly</b> cloud resource usage and enter the dollar amount below. Note these estimates are for initial approval only. After the request is approved, you will be asked to provide a valid Task Order number with specific CLIN amounts for cloud services.',
    )

    dollar_value = IntegerField(
        "Total Spend",
        description="What is your total expected budget for this JEDI Cloud Request?",
    )

    number_user_sessions = IntegerField(
        description="How many user sessions do you expect on these systems each day?"
    )

    average_daily_traffic = IntegerField(
        "Average Daily Traffic (Number of Requests)",
        description="What is the average daily traffic you expect the systems under this cloud contract to use?",
    )

    average_daily_traffic_gb = IntegerField(
        "Average Daily Traffic (GB)",
        description="What is the average daily traffic you expect the systems under this cloud contract to use?",
    )

    start_date = DateField(
        description="When do you expect to start using the JEDI Cloud (not for billing purposes)?",
        validators=[
            InputRequired(),
            DateRange(
                lower_bound=pendulum.duration(days=1),
                upper_bound=None,
                message="Must be a date in the future.",
            ),
        ],
        format="%m/%d/%Y",
    )

    name = StringField(
        "Name Your Request",
        description="This name serves as a reference for your initial request and the associated workspace that will be created once this request is approved. You may edit this name later.",
        validators=[
            InputRequired(),
            Length(
                min=4,
                max=100,
                message="Request names must be at least 4 and not more than 100 characters",
            ),
        ],
    )


class InformationAboutYouForm(ValidatedForm):
    fname_request = inherit_field(USER_FIELDS["first_name"])

    lname_request = inherit_field(USER_FIELDS["last_name"])

    email_request = EmailField("E-mail Address", validators=[InputRequired(), Email()])

    phone_number = inherit_field(USER_FIELDS["phone_number"])

    service_branch = inherit_field(USER_FIELDS["service_branch"])

    citizenship = inherit_field(USER_FIELDS["citizenship"])

    designation = inherit_field(USER_FIELDS["designation"])

    date_latest_training = inherit_field(USER_FIELDS["date_latest_training"])


class WorkspaceOwnerForm(ValidatedForm):
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

    fname_poc = StringField("First Name", validators=[InputRequired()])

    lname_poc = StringField("Last Name", validators=[InputRequired()])

    email_poc = EmailField("Email Address", validators=[InputRequired(), Email()])

    dodid_poc = StringField(
        "DoD ID", validators=[InputRequired(), Length(min=10), IsNumber()]
    )


class ReviewAndSubmitForm(ValidatedForm):
    reviewed = BooleanField("I have reviewed this data and it is correct.")
