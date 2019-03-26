from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import Required, Email, Length, Optional
from wtforms.fields import StringField, FormField, FieldList, HiddenField

from atst.domain.permission_sets import PermissionSets
from .forms import BaseForm
from atst.forms.validators import IsNumber, PhoneNumber
from atst.forms.fields import SelectField
from atst.utils.localization import translate


class PermissionsForm(BaseForm):
    member = StringField()
    user_id = HiddenField()
    perms_app_mgmt = SelectField(
        None,
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT, "View only"),
            (PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT, "Edit access"),
        ],
    )
    perms_funding = SelectField(
        None,
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_FUNDING, "View only"),
            (PermissionSets.EDIT_PORTFOLIO_FUNDING, "Edit access"),
        ],
    )
    perms_reporting = SelectField(
        None,
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_REPORTS, "View only"),
            (PermissionSets.EDIT_PORTFOLIO_REPORTS, "Edit access"),
        ],
    )
    perms_portfolio_mgmt = SelectField(
        None,
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_ADMIN, "View only"),
            (PermissionSets.EDIT_PORTFOLIO_ADMIN, "Edit access"),
        ],
    )

    @property
    def data(self):
        _data = super().data
        _data["permission_sets"] = []
        for field in _data:
            if "perms" in field:
                _data["permission_sets"].append(_data[field])

        return _data


class MembersPermissionsForm(BaseForm):
    members_permissions = FieldList(FormField(PermissionsForm))


class EditForm(PermissionsForm):
    # This form also accepts a field for each environment in each application
    #  that the user is a member of
    pass


class NewForm(PermissionsForm):
    first_name = StringField(
        label=translate("forms.new_member.first_name_label"), validators=[Required()]
    )
    last_name = StringField(
        label=translate("forms.new_member.last_name_label"), validators=[Required()]
    )
    email = EmailField(
        translate("forms.new_member.email_label"), validators=[Required(), Email()]
    )
    phone_number = TelField(
        translate("forms.new_member.phone_number_label"),
        validators=[Optional(), PhoneNumber()],
    )
    dod_id = StringField(
        translate("forms.new_member.dod_id_label"),
        validators=[Required(), Length(min=10), IsNumber()],
    )


class AssignPPOCForm(PermissionsForm):
    user_id = SelectField(
        label=translate("forms.assign_ppoc.dod_id"), validators=[Required()]
    )
