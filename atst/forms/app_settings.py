from wtforms.fields import StringField, HiddenField, RadioField, FieldList, FormField

from .forms import BaseForm
from .data import ENV_ROLES


class EnvMemberRoleForm(BaseForm):
    name = StringField()
    user_id = HiddenField()
    role = RadioField(choices=ENV_ROLES, coerce=BaseForm.remove_empty_string)


class EnvironmentRolesForm(BaseForm):
    team_roles = FieldList(FormField(EnvMemberRoleForm))
    env_id = HiddenField()
