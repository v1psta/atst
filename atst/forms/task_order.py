from wtforms.fields import (
    DateField,
    IntegerField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)

from .forms import CacheableForm
from .data import (
    SERVICE_BRANCHES,
    APP_MIGRATION,
    PROJECT_COMPLEXITY,
    DEV_TEAM,
    TEAM_EXPERIENCE,
)


class TaskOrderForm(CacheableForm):
    scope = TextAreaField(
        "Cloud Project Scope",
        description="The name of your office or organization. You can add multiple applications to your portfolio. Your task orders are used to pay for these applications and their environments",
    )
    defense_component = SelectField(
        "Department of Defense Component",
        description="Your team's plan for using the cloud, such as migrating an existing application or creating a prototype.",
        choices=SERVICE_BRANCHES,
    )
    app_migration = RadioField(
        "App Migration",
        description="Do you plan to migrate existing application(s) to the cloud?",
        choices=APP_MIGRATION,
        default="",
    )
    native_apps = RadioField(
        "Native Apps",
        description="Do you plan to develop application(s) natively in the cloud? ",
        choices=[("yes", "Yes"), ("no", "No"), ("not_sure", "Not Sure")],
    )
    complexity = SelectMultipleField(
        "Project Complexity",
        description="Which of these describes how complex your team's use of the cloud will be? (Select all that apply.)",
        choices=PROJECT_COMPLEXITY,
        default="",
    )
    complexity_other = StringField("?")
    dev_team = SelectMultipleField(
        "Development Team",
        description="Which people or teams will be completing the development work for your cloud applications?",
        choices=DEV_TEAM,
        default="",
    )
    dev_team_other = StringField("?")
    team_experience = RadioField(
        "Team Experience",
        description="How much experience does your team have with development in the cloud?",
        choices=TEAM_EXPERIENCE,
        default="",
    )
    start_date = DateField(
        "Period of Performance",
        description="Select a start and end date for your Task Order to be active. Please note, this will likely be revised once your Task Order has been approved.",
    )
    end_date = DateField("Period of Performance")
    clin_01 = IntegerField(
        "CLIN 01 : Unclassified Cloud Offerings",
        description="UNCLASSIFIED Infrastructure as a Service (IaaS) and Platform as a Service (PaaS) offerings. ",
    )
    clin_02 = IntegerField(
        "CLIN 02: Classified Cloud Offerings",
        description="CLASSIFIED Infrastructure as a Service (IaaS) and Platform as a Service (PaaS) offerings. ",
    )
    clin_03 = IntegerField(
        "CLIN 03: Unclassified Cloud Support and Assistance",
        description="UNCLASSIFIED technical guidance from the cloud service provider, including architecture, configuration of IaaS and PaaS, integration, troubleshooting assistance, and other services.",
    )
    clin_04 = IntegerField(
        "CLIN 04: Classified Cloud Support and Assistance",
        description="CLASSIFIED technical guidance from the cloud service provider, including architecture, configuration of IaaS and PaaS, integration, troubleshooting assistance, and other services.",
    )
    ko_first_name = StringField("First Name")
    ko_last_name = StringField("Last Name")
    ko_email = StringField("Email")
    ko_dod_id = StringField("DOD ID")
    cor_first_name = StringField("First Name")
    cor_last_name = StringField("Last Name")
    cor_email = StringField("Email")
    cor_dod_id = StringField("DOD ID")
    so_first_name = StringField("First Name")
    so_last_name = StringField("Last Name")
    so_email = StringField("Email")
    so_dod_id = StringField("DOD ID")
    number = StringField("Task Order Number")
    loa = StringField("Line of Accounting (LOA)")
