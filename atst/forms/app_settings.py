from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField, HiddenField, RadioField

from .forms import BaseForm
from .data import ENV_ROLES


class EnvMemberRoleForm(FlaskForm):
    user_id = HiddenField()
    role = RadioField(choices=ENV_ROLES, default="no_access")

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        return _data


class EnvironmentRolesForm(BaseForm):
    team_roles = FieldList(FormField(EnvMemberRoleForm))
    env_id = HiddenField()
