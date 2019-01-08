from wtforms.fields import (
    BooleanField,
    IntegerField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.fields.html5 import DateField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Required, Length

from atst.forms.validators import IsNumber

from .forms import CacheableForm
from .data import (
    SERVICE_BRANCHES,
    APP_MIGRATION,
    PROJECT_COMPLEXITY,
    DEV_TEAM,
    TEAM_EXPERIENCE,
)


class AppInfoForm(CacheableForm):
    portfolio_name = StringField(
        "Organization Portfolio Name",
        description="The name of your office or organization. You can add multiple applications to your portfolio. Your task orders are used to pay for these applications and their environments",
    )
    scope = TextAreaField(
        "Cloud Project Scope",
        description="Your team's plan for using the cloud, such as migrating an existing application or creating a prototype.",
    )
    defense_component = SelectField(
        "Department of Defense Component", choices=SERVICE_BRANCHES
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
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    complexity_other = StringField("Project Complexity Other")
    dev_team = SelectMultipleField(
        "Development Team",
        description="Which people or teams will be completing the development work for your cloud applications?",
        choices=DEV_TEAM,
        default="",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    dev_team_other = StringField("Development Team Other")
    team_experience = RadioField(
        "Team Experience",
        description="How much experience does your team have with development in the cloud?",
        choices=TEAM_EXPERIENCE,
        default="",
    )


class FundingForm(CacheableForm):
    start_date = DateField("Start Date", format="%m/%d/%Y")
    end_date = DateField("End Date", format="%m/%d/%Y")
    clin_01 = IntegerField("CLIN 01 : Unclassified")
    clin_02 = IntegerField("CLIN 02: Classified")
    clin_03 = IntegerField("CLIN 03: Unclassified")
    clin_04 = IntegerField("CLIN 04: Classified")


class UnclassifiedFundingForm(FundingForm):
    clin_02 = IntegerField("CLIN 02: Classified (available soon)")
    clin_04 = IntegerField("CLIN 04: Classified (available soon)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clin_02.data = "0"
        self.clin_04.data = "0"


class OversightForm(CacheableForm):
    ko_first_name = StringField("First Name")
    ko_last_name = StringField("Last Name")
    ko_email = StringField("Email")
    ko_dod_id = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )

    cor_first_name = StringField("First Name")
    cor_last_name = StringField("Last Name")
    cor_email = StringField("Email")
    cor_dod_id = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )

    so_first_name = StringField("First Name")
    so_last_name = StringField("Last Name")
    so_email = StringField("Email")
    so_dod_id = StringField(
        "DOD ID", validators=[Required(), Length(min=10), IsNumber()]
    )

    ko_invite = BooleanField(
        "Invite KO to Task Order Builder",
        description="""
            Your KO will need to approve funding for this Task Order by logging
            into the JEDI Cloud Portal, submitting the Task Order documents
            within their official system of record, and electronically signing.
            <i>You may choose to skip this for now and invite them later.</i>
            """,
    )
    cor_invite = BooleanField(
        "Invite COR to Task Order Builder",
        description="""
            Your COR may assist with submitting the Task Order documents within
            their official system of record. <i>You may choose to skip this for
            now and invite them later.</i>
            """,
    )
    so_invite = BooleanField(
        "Invite Security Officer to Task Order Builder",
        description="""
            Your Security Officer will need to answer some security
            configuration questions in order to generate a DD-254 document,
            then electronically sign. <i>You may choose to skip this for now
            and invite them later.</i>
            """,
    )


class ReviewForm(CacheableForm):
    pass
