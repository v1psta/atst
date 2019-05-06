from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField, HiddenField, RadioField, StringField

from .forms import BaseForm
from .data import ENV_ROLES


class MemberForm(FlaskForm):
    user_id = HiddenField()
    user_name = StringField()
    role = RadioField(choices=ENV_ROLES, default="no_access")

    @property
    def data(self):
        _data = super().data
        for field in _data:
            if field == "role" and _data[field] == "no_access":
                _data[field] = None
        return _data


class RoleForm(FlaskForm):
    role = HiddenField()
    members = FieldList(FormField(MemberForm))


class EnvironmentRolesForm(FlaskForm):
    team_roles = FieldList(FormField(RoleForm))
    env_id = HiddenField()


class AppEnvRolesForm(BaseForm):
    envs = FieldList(FormField(EnvironmentRolesForm))
