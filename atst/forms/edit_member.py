from flask_wtf import FlaskForm
from wtforms.validators import Optional

from atst.forms.fields import SelectField

from .data import WORKSPACE_ROLES, ENVIRONMENT_ROLES


class EditMemberForm(FlaskForm):

    workspace_role = SelectField(
        "Workspace Role", choices=WORKSPACE_ROLES, validators=[Optional()]
    )

    environment_role = SelectField(
        "Environment Role", choices=ENVIRONMENT_ROLES, validators=[Optional()]
    )
