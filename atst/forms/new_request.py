import pendulum
from wtforms.fields.html5 import DateField, EmailField, IntegerField
from wtforms.fields import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import Email, Length, Optional, InputRequired, DataRequired

from .fields import SelectField
from .forms import CacheableForm
from .edit_user import USER_FIELDS, inherit_field
from .data import (
    SERVICE_BRANCHES,
    ASSISTANCE_ORG_TYPES,
    DATA_TRANSFER_AMOUNTS,
    COMPLETION_DATE_RANGES,
)
from .validators import DateRange, IsNumber
from atst.domain.requests import Requests
from atst.utils.localization import translate


class DetailsOfUseForm(CacheableForm):
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

        if annual_spend > Requests.ANNUAL_SPEND_THRESHOLD:
            self.number_user_sessions.validators.append(InputRequired())
            self.average_daily_traffic.validators.append(InputRequired())

        return super(DetailsOfUseForm, self).validate(*args, **kwargs)

    # Details of Use: General
    dod_component = SelectField(
        translate("forms.new_request.dod_component_label"),
        description=translate("forms.new_request.dod_component_description"),
        choices=SERVICE_BRANCHES,
        validators=[InputRequired()],
    )

    jedi_usage = TextAreaField(
        translate("forms.new_request.jedi_usage_label"),
        description=translate("forms.new_request.jedi_usage_description"),
        validators=[InputRequired()],
    )

    # Details of Use: Cloud Readiness
    num_software_systems = IntegerField(
        translate("forms.new_request.num_software_systems_label"),
        description=translate("forms.new_request.num_software_systems_description"),
    )

    jedi_migration = RadioField(
        translate("forms.new_request.jedi_migration_label"),
        description=translate("forms.new_request.jedi_migration_description"),
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    rationalization_software_systems = RadioField(
        description=translate(
            "forms.new_request.rationalization_software_systems_description"
        ),
        choices=[("yes", "Yes"), ("no", "No"), ("In Progress", "In Progress")],
        default="",
    )

    technical_support_team = RadioField(
        description=translate("forms.new_request.technical_support_team_description"),
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    organization_providing_assistance = RadioField(  # this needs to be updated to use checkboxes instead of radio
        description=translate(
            "forms.new_request.organization_providing_assistance_description"
        ),
        choices=ASSISTANCE_ORG_TYPES,
        default="",
    )

    engineering_assessment = RadioField(
        description=translate("forms.new_request.engineering_assessment_description"),
        choices=[("yes", "Yes"), ("no", "No"), ("In Progress", "In Progress")],
        default="",
    )

    data_transfers = SelectField(
        description=translate("forms.new_request.data_transfers_description"),
        choices=DATA_TRANSFER_AMOUNTS,
        validators=[DataRequired()],
    )

    expected_completion_date = SelectField(
        description=translate("forms.new_request.expected_completion_date_description"),
        choices=COMPLETION_DATE_RANGES,
        validators=[DataRequired()],
    )

    cloud_native = RadioField(
        description=translate("forms.new_request.cloud_native_description"),
        choices=[("yes", "Yes"), ("no", "No")],
        default="",
    )

    # Details of Use: Financial Usage
    estimated_monthly_spend = IntegerField(
        translate("forms.new_request.estimated_monthly_spend_label"),
        description=translate("forms.new_request.estimated_monthly_spend_description"),
    )

    dollar_value = IntegerField(
        translate("forms.new_request.dollar_value_label"),
        description=translate("forms.new_request.dollar_value_description"),
    )

    number_user_sessions = IntegerField(
        description=translate("forms.new_request.number_user_sessions_description")
    )

    average_daily_traffic = IntegerField(
        translate("forms.new_request.average_daily_traffic_label"),
        description=translate("forms.new_request.average_daily_traffic_description"),
    )

    average_daily_traffic_gb = IntegerField(
        translate("forms.new_request.average_daily_traffic_gb_label"),
        description=translate("forms.new_request.average_daily_traffic_gb_description"),
    )

    start_date = DateField(
        description=translate("forms.new_request.start_date_label"),
        validators=[
            InputRequired(),
            DateRange(
                lower_bound=pendulum.duration(days=1),
                upper_bound=None,
                message=translate(
                    "forms.new_request.start_date_date_range_validation_message"
                ),
            ),
        ],
        format="%m/%d/%Y",
    )

    name = StringField(
        translate("forms.new_request.name_label"),
        description=translate("forms.new_request.name_description"),
        validators=[
            InputRequired(),
            Length(
                min=4,
                max=100,
                message=translate("forms.new_request.name_length_validation_message"),
            ),
        ],
    )


class InformationAboutYouForm(CacheableForm):
    fname_request = inherit_field(USER_FIELDS["first_name"])
    lname_request = inherit_field(USER_FIELDS["last_name"])
    email_request = inherit_field(USER_FIELDS["email"])
    phone_number = inherit_field(USER_FIELDS["phone_number"])
    phone_ext = inherit_field(USER_FIELDS["phone_ext"], required=False)
    service_branch = inherit_field(USER_FIELDS["service_branch"])
    citizenship = inherit_field(USER_FIELDS["citizenship"])
    designation = inherit_field(USER_FIELDS["designation"])
    date_latest_training = inherit_field(USER_FIELDS["date_latest_training"])


class WorkspaceOwnerForm(CacheableForm):
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
        translate("forms.new_request.am_poc_label"),
        default=False,
        false_values=(False, "false", "False", "no", ""),
    )

    fname_poc = StringField(
        translate("forms.new_request.fname_poc_label"), validators=[InputRequired()]
    )

    lname_poc = StringField(
        translate("forms.new_request.lname_poc_label"), validators=[InputRequired()]
    )

    email_poc = EmailField(
        translate("forms.new_request.email_poc_label"),
        validators=[InputRequired(), Email()],
    )

    dodid_poc = StringField(
        translate("forms.new_request.dodid_poc_label"),
        validators=[InputRequired(), Length(min=10), IsNumber()],
    )


class ReviewAndSubmitForm(CacheableForm):
    reviewed = BooleanField(translate("forms.new_request.reviewed_label"))
