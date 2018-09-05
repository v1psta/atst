from flask_wtf import Form
from wtforms.validators import Optional

from atst.forms.fields import SelectField

from .data import WORKSPACE_ROLES


class UpdateMemberForm(Form):

    workspace_role = SelectField(
        "Workspace Role", choices=WORKSPACE_ROLES, validators=[Optional()], default=""
    )
