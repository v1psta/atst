from wtforms.validators import Required
from wtforms.fields import StringField, FormField, FieldList, HiddenField

from atst.domain.permission_sets import PermissionSets
from .forms import BaseForm
from .member import NewForm as BaseNewMemberForm
from atst.forms.fields import SelectField
from atst.utils.localization import translate


class PermissionsForm(BaseForm):
    member = StringField()
    user_id = HiddenField()
    perms_app_mgmt = SelectField(
        translate("forms.new_member.app_mgmt"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT, "View"),
            (PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT, "Edit"),
        ],
    )
    perms_funding = SelectField(
        translate("forms.new_member.funding"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_FUNDING, "View"),
            (PermissionSets.EDIT_PORTFOLIO_FUNDING, "Edit"),
        ],
    )
    perms_reporting = SelectField(
        translate("forms.new_member.reporting"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_REPORTS, "View"),
            (PermissionSets.EDIT_PORTFOLIO_REPORTS, "Edit"),
        ],
    )
    perms_portfolio_mgmt = SelectField(
        translate("forms.new_member.portfolio_mgmt"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_ADMIN, "View"),
            (PermissionSets.EDIT_PORTFOLIO_ADMIN, "Edit"),
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


class NewForm(BaseForm):
    user_data = FormField(BaseNewMemberForm)
    permission_sets = FormField(PermissionsForm)

    @property
    def update_data(self):
        return {
            "permission_sets": self.data.get("permission_sets").get("permission_sets"),
            **self.data.get("user_data"),
        }


class AssignPPOCForm(PermissionsForm):
    user_id = SelectField(
        label=translate("forms.assign_ppoc.dod_id"),
        validators=[Required()],
        choices=[("", "- Select -")],
    )
