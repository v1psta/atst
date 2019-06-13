from wtforms.validators import Required
from wtforms.fields import StringField, FormField, FieldList, HiddenField

from atst.domain.permission_sets import PermissionSets
from .forms import BaseForm
from .member import NewForm as BaseNewMemberForm
from atst.forms.fields import SelectField
from atst.utils.localization import translate


class PermissionsForm(BaseForm):
    member_name = StringField()
    member_id = HiddenField()
    perms_app_mgmt = SelectField(
        translate("forms.new_member.app_mgmt"),
        choices=[
            (
                PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
                translate("common.view"),
            ),
            (
                PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
                translate("common.edit"),
            ),
        ],
    )
    perms_funding = SelectField(
        translate("forms.new_member.funding"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_FUNDING, translate("common.view")),
            (PermissionSets.EDIT_PORTFOLIO_FUNDING, translate("common.edit")),
        ],
    )
    perms_reporting = SelectField(
        translate("forms.new_member.reporting"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_REPORTS, translate("common.view")),
            (PermissionSets.EDIT_PORTFOLIO_REPORTS, translate("common.edit")),
        ],
    )
    perms_portfolio_mgmt = SelectField(
        translate("forms.new_member.portfolio_mgmt"),
        choices=[
            (PermissionSets.VIEW_PORTFOLIO_ADMIN, translate("common.view")),
            (PermissionSets.EDIT_PORTFOLIO_ADMIN, translate("common.edit")),
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
    role_id = SelectField(
        label=translate("forms.assign_ppoc.dod_id"),
        validators=[Required()],
        choices=[("", "- Select -")],
    )
