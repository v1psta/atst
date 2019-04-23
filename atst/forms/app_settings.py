from wtforms.fields import StringField, HiddenField, RadioField, FieldList, FormField

from .forms import BaseForm
from .data import ENV_ROLES


class EnvMemberRoleForm(BaseForm):
    name = StringField()
    user_id = HiddenField()
    role = RadioField(choices=ENV_ROLES)

    @property
    def data(self):
        _data = super().data
        if _data["role"] == "":
            _data["role"] = None
        return _data


class EnvironmentRolesForm(BaseForm):
    team_roles = FieldList(FormField(EnvMemberRoleForm))
    env_id = HiddenField()
