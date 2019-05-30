from wtforms.fields import (
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
)
from wtforms.validators import Length, Optional
from wtforms.widgets import ListWidget, CheckboxInput

from .forms import BaseForm
from atst.utils.localization import translate

from .data import (
    APPLICATION_COMPLEXITY,
    APP_MIGRATION,
    DEV_TEAM,
    SERVICE_BRANCHES,
    TEAM_EXPERIENCE,
)


class PortfolioForm(BaseForm):
    name = StringField(
        translate("forms.portfolio.name_label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name_length_validation_message"),
            )
        ],
    )


class PortfolioCreationForm(BaseForm):
    name = StringField(
        translate("forms.portfolio.name_label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name_length_validation_message"),
            )
        ],
    )

    defense_component = SelectField(
        translate("forms.task_order.defense_component_label"),
        choices=SERVICE_BRANCHES,
        default="",
        filters=[BaseForm.remove_empty_string],
    )

    description = TextAreaField(
        translate("forms.task_order.scope_label"),
        description=translate("forms.task_order.scope_description"),
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
        filters=[BaseForm.remove_empty_string],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )

    complexity_other = StringField(
        translate("forms.task_order.complexity_other_label"),
        default=None,
        filters=[BaseForm.remove_empty_string],
    )

    dev_team = SelectMultipleField(
        translate("forms.task_order.dev_team.label"),
        description=translate("forms.task_order.dev_team.description"),
        choices=DEV_TEAM,
        default=None,
        filters=[BaseForm.remove_empty_string],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )

    dev_team_other = StringField(
        translate("forms.task_order.dev_team_other_label"),
        default=None,
        filters=[BaseForm.remove_empty_string],
    )

    team_experience = RadioField(
        translate("forms.task_order.team_experience.label"),
        description=translate("forms.task_order.team_experience.description"),
        choices=TEAM_EXPERIENCE,
        default="",
        validators=[Optional()],
    )
