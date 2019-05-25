from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField, HiddenField, RadioField, StringField

from .forms import BaseForm
from .data import ENV_ROLES, ENV_ROLE_NO_ACCESS as NO_ACCESS
from atst.forms.fields import EncryptedHiddenField


class MemberForm(FlaskForm):
    application_role_id = EncryptedHiddenField()
    user_name = StringField()
    role_name = RadioField(choices=ENV_ROLES, default=NO_ACCESS)

    @property
    def data(self):
        _data = super().data
        if "role_name" in _data and _data["role_name"] == NO_ACCESS:
            _data["role_name"] = None
        return _data


class RoleForm(FlaskForm):
    role = HiddenField()
    members = FieldList(FormField(MemberForm))


class EnvironmentRolesForm(FlaskForm):
    team_roles = FieldList(FormField(RoleForm))
    env_id = HiddenField()


class AppEnvRolesForm(BaseForm):
    envs = FieldList(FormField(EnvironmentRolesForm))
