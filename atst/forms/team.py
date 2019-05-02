from flask_wtf import FlaskForm
from wtforms.fields import FormField, FieldList, HiddenField, StringField

from .application_member import EnvironmentForm
from .forms import BaseForm
from atst.forms.fields import SelectField
from atst.domain.permission_sets import PermissionSets
from atst.utils.localization import translate


class PermissionsForm(FlaskForm):
    perms_env_mgmt = SelectField(
        translate("portfolios.applications.members.new.manage_envs"),
        choices=[
            ("", "View only"),
            (PermissionSets.EDIT_APPLICATION_ENVIRONMENTS, "Edit access"),
        ],
    )
    perms_team_mgmt = SelectField(
        translate("portfolios.applications.members.new.manage_team"),
        choices=[
            ("", "View only"),
            (PermissionSets.EDIT_APPLICATION_TEAM, "Edit access"),
        ],
    )
    perms_del_env = SelectField(
        choices=[("", "No"), (PermissionSets.DELETE_APPLICATION_ENVIRONMENTS, "Yes")]
    )

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        permission_sets = []
        for field in _data:
            if _data[field] is not None:
                permission_sets.append(_data[field])

        return permission_sets


class MemberForm(FlaskForm):
    user_id = HiddenField()
    user_name = StringField()
    environment_roles = FieldList(FormField(EnvironmentForm))
    permission_sets = FormField(PermissionsForm)

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)

        return _data


class TeamForm(BaseForm):
    members = FieldList(FormField(MemberForm))
