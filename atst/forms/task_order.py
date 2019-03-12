from wtforms.fields import (
    BooleanField,
    DecimalField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    FileField,
)
from wtforms.fields.html5 import DateField, TelField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Email, Length, Required, Optional
from flask_wtf.file import FileAllowed

from atst.forms.validators import IsNumber, PhoneNumber, RequiredIf

from .forms import BaseForm
from .data import (
    SERVICE_BRANCHES,
    APP_MIGRATION,
    APPLICATION_COMPLEXITY,
    DEV_TEAM,
    TEAM_EXPERIENCE,
    PERIOD_OF_PERFORMANCE_LENGTH,
)
from atst.utils.localization import translate


class AppInfoWithExistingPortfolioForm(BaseForm):
    scope = TextAreaField(
        translate("forms.task_order.scope_label"),
        description=translate("forms.task_order.scope_description"),
    )
    defense_component = SelectField(
        translate("forms.task_order.defense_component_label"), choices=SERVICE_BRANCHES
    )
    app_migration = RadioField(
        translate("forms.task_order.app_migration.label"),
        description=translate("forms.task_order.app_migration.description"),
        choices=APP_MIGRATION,
        default="",
        validators=[Optional()],
    )
    native_apps = RadioField(
        translate("forms.task_order.native_apps.label"),
        description=translate("forms.task_order.native_apps.description"),
        choices=[("yes", "Yes"), ("no", "No"), ("not_sure", "Not Sure")],
        default="",
        validators=[Optional()],
    )
    complexity = SelectMultipleField(
        translate("forms.task_order.complexity.label"),
        description=translate("forms.task_order.complexity.description"),
        choices=APPLICATION_COMPLEXITY,
        default=None,
        filters=[lambda x: x or None],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    complexity_other = StringField(
        translate("forms.task_order.complexity_other_label"),
        default=None,
        filters=[lambda x: x or None],
    )
    dev_team = SelectMultipleField(
        translate("forms.task_order.dev_team.label"),
        description=translate("forms.task_order.dev_team.description"),
        choices=DEV_TEAM,
        default=None,
        filters=[lambda x: x or None],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    dev_team_other = StringField(
        translate("forms.task_order.dev_team_other_label"),
        default=None,
        filters=[lambda x: x or None],
    )
    team_experience = RadioField(
        translate("forms.task_order.team_experience.label"),
        description=translate("forms.task_order.team_experience.description"),
        choices=TEAM_EXPERIENCE,
        default="",
        validators=[Optional()],
    )


class AppInfoForm(AppInfoWithExistingPortfolioForm):
    portfolio_name = StringField(
        translate("forms.task_order.portfolio_name_label"),
        description=translate("forms.task_order.portfolio_name_description"),
        filters=[lambda x: x or None],
        validators=[
            Required(),
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name_length_validation_message"),
            ),
        ],
    )
    defense_component = SelectField(
        translate("forms.task_order.defense_component_label"),
        choices=SERVICE_BRANCHES,
        default="",
        filters=[lambda x: x or None],
    )


class FundingForm(BaseForm):
    performance_length = SelectField(
        translate("forms.task_order.performance_length.label"),
        choices=PERIOD_OF_PERFORMANCE_LENGTH,
    )
    start_date = DateField(
        translate("forms.task_order.start_date_label"), format="%m/%d/%Y"
    )
    end_date = DateField(
        translate("forms.task_order.end_date_label"), format="%m/%d/%Y"
    )
    csp_estimate = FileField(
        translate("forms.task_order.csp_estimate_label"),
        description=translate("forms.task_order.csp_estimate_description"),
        validators=[
            FileAllowed(
                ["pdf", "png"], translate("forms.task_order.file_format_not_allowed")
            )
        ],
        render_kw={"accept": ".pdf,.png,application/pdf,image/png"},
    )
    clin_01 = DecimalField(
        translate("forms.task_order.clin_01_label"), validators=[Optional()]
    )
    clin_02 = DecimalField(
        translate("forms.task_order.clin_02_label"), validators=[Optional()]
    )
    clin_03 = DecimalField(
        translate("forms.task_order.clin_03_label"), validators=[Optional()]
    )
    clin_04 = DecimalField(
        translate("forms.task_order.clin_04_label"), validators=[Optional()]
    )


class UnclassifiedFundingForm(FundingForm):
    clin_02 = StringField(
        translate("forms.task_order.unclassified_clin_02_label"),
        filters=[lambda x: x or None],
    )
    clin_04 = StringField(
        translate("forms.task_order.unclassified_clin_04_label"),
        filters=[lambda x: x or None],
    )


class OversightForm(BaseForm):
    ko_first_name = StringField(
        translate("forms.task_order.oversight_first_name_label"),
        filters=[lambda x: x or None],
    )
    ko_last_name = StringField(
        translate("forms.task_order.oversight_last_name_label"),
        filters=[lambda x: x or None],
    )
    ko_email = StringField(
        translate("forms.task_order.oversight_email_label"),
        validators=[Optional(), Email()],
        filters=[lambda x: x or None],
    )
    ko_phone_number = TelField(
        translate("forms.task_order.oversight_phone_label"),
        validators=[Optional(), PhoneNumber()],
        filters=[lambda x: x or None],
    )
    ko_dod_id = StringField(
        translate("forms.task_order.oversight_dod_id_label"),
        filters=[lambda x: x or None],
        validators=[
            RequiredIf(lambda form: form._fields.get("ko_invite").data),
            Length(min=10),
            IsNumber(),
        ],
    )

    am_cor = BooleanField(translate("forms.task_order.oversight_am_cor_label"))
    cor_first_name = StringField(
        translate("forms.task_order.oversight_first_name_label"),
        filters=[lambda x: x or None],
    )
    cor_last_name = StringField(
        translate("forms.task_order.oversight_last_name_label"),
        filters=[lambda x: x or None],
    )
    cor_email = StringField(
        translate("forms.task_order.oversight_email_label"),
        filters=[lambda x: x or None],
        validators=[Optional(), Email()],
    )
    cor_phone_number = TelField(
        translate("forms.task_order.oversight_phone_label"),
        filters=[lambda x: x or None],
        validators=[
            RequiredIf(lambda form: not form._fields.get("am_cor").data),
            Optional(),
            PhoneNumber(),
        ],
    )
    cor_dod_id = StringField(
        translate("forms.task_order.oversight_dod_id_label"),
        filters=[lambda x: x or None],
        validators=[
            RequiredIf(
                lambda form: not form._fields.get("am_cor").data
                and form._fields.get("cor_invite").data
            ),
            Length(min=10),
            IsNumber(),
        ],
    )

    so_first_name = StringField(
        translate("forms.task_order.oversight_first_name_label"),
        filters=[lambda x: x or None],
    )
    so_last_name = StringField(
        translate("forms.task_order.oversight_last_name_label"),
        filters=[lambda x: x or None],
    )
    so_email = StringField(
        translate("forms.task_order.oversight_email_label"),
        filters=[lambda x: x or None],
        validators=[Optional(), Email()],
    )
    so_phone_number = TelField(
        translate("forms.task_order.oversight_phone_label"),
        filters=[lambda x: x or None],
        validators=[Optional(), PhoneNumber()],
    )
    so_dod_id = StringField(
        translate("forms.task_order.oversight_dod_id_label"),
        filters=[lambda x: x or None],
        validators=[
            RequiredIf(lambda form: form._fields.get("so_invite").data),
            Length(min=10),
            IsNumber(),
        ],
    )

    ko_invite = BooleanField(
        translate("forms.task_order.ko_invite_label"),
        description=translate("forms.task_order.skip_invite_description"),
    )
    cor_invite = BooleanField(
        translate("forms.task_order.cor_invite_label"),
        description=translate("forms.task_order.skip_invite_description"),
    )
    so_invite = BooleanField(
        translate("forms.task_order.so_invite_label"),
        description=translate("forms.task_order.skip_invite_description"),
    )


class ReviewForm(BaseForm):
    pass


class SignatureForm(BaseForm):
    level_of_warrant = DecimalField(
        translate("task_orders.sign.level_of_warrant_label"),
        description=translate("task_orders.sign.level_of_warrant_description"),
        validators=[
            RequiredIf(
                lambda form: (
                    form._fields.get("unlimited_level_of_warrant").data is not True
                )
            )
        ],
    )

    unlimited_level_of_warrant = BooleanField(
        translate("task_orders.sign.unlimited_level_of_warrant_description"),
        validators=[Optional()],
    )

    signature = BooleanField(
        translate("task_orders.sign.digital_signature_label"),
        description=translate("task_orders.sign.digital_signature_description"),
        validators=[Required()],
    )
