from wtforms.fields import (
    BooleanField,
    IntegerField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    FileField,
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
    PERIOD_OF_PERFORMANCE_LENGTH,
)
from atst.utils.localization import translate


class AppInfoForm(CacheableForm):
    portfolio_name = StringField(
        translate("forms.task_order.portfolio_name_label"),
        description=translate("forms.task_order.portfolio_name_description"),
    )
    scope = TextAreaField(
        translate("forms.task_order.scope_label"),
        description=translate("forms.task_order.scope_description"),
    )
    defense_component = SelectField(
        translate("forms.task_order.defense_component_label"), choices=SERVICE_BRANCHES
    )
    app_migration = RadioField(
        translate("forms.task_order.app_migration_label"),
        description=translate("forms.task_order.app_migration_description"),
        choices=APP_MIGRATION,
        default="",
    )
    native_apps = RadioField(
        translate("forms.task_order.native_apps_label"),
        description=translate("forms.task_order.native_apps_description"),
        choices=[("yes", "Yes"), ("no", "No"), ("not_sure", "Not Sure")],
    )
    complexity = SelectMultipleField(
        translate("forms.task_order.complexity_label"),
        description=translate("forms.task_order.complexity_description"),
        choices=PROJECT_COMPLEXITY,
        default="",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    complexity_other = StringField(translate("forms.task_order.complexity_other_label"))
    dev_team = SelectMultipleField(
        translate("forms.task_order.dev_team_label"),
        description=translate("forms.task_order.dev_team_description"),
        choices=DEV_TEAM,
        default="",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    dev_team_other = StringField(translate("forms.task_order.dev_team_other_label"))
    team_experience = RadioField(
        translate("forms.task_order.team_experience_label"),
        description=translate("forms.task_order.team_experience_description"),
        choices=TEAM_EXPERIENCE,
        default="",
    )


class FundingForm(CacheableForm):
    performance_length = SelectField(
        translate("forms.task_order.performance_length_label"),
        choices=PERIOD_OF_PERFORMANCE_LENGTH,
    )
    start_date = DateField(
        translate("forms.task_order.start_date_label"), format="%m/%d/%Y"
    )
    end_date = DateField(
        translate("forms.task_order.end_date_label"), format="%m/%d/%Y"
    )
    csp_cost_estimate = FileField(
        translate("forms.task_order.csp_cost_est_label"),
        description=translate("forms.task_order.csp_cost_est_description"),
    )
    clin_01 = IntegerField(translate("forms.task_order.clin_01_label"))
    clin_02 = IntegerField(translate("forms.task_order.clin_02_label"))
    clin_03 = IntegerField(translate("forms.task_order.clin_03_label"))
    clin_04 = IntegerField(translate("forms.task_order.clin_04_label"))


class UnclassifiedFundingForm(FundingForm):
    clin_02 = IntegerField(translate("forms.task_order.unclassified_clin_02_label"))
    clin_04 = IntegerField(translate("forms.task_order.unclassified_clin_04_label")

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
