from flask_wtf import FlaskForm
from wtforms.validators import Required

from atst.forms.fields import SelectField

from .data import WORKSPACE_ROLES


class EditMemberForm(FlaskForm):
    # This form also accepts a field for each environment in each project
    #  that the user is a member of

    workspace_role = SelectField(
        "Workspace Role", choices=WORKSPACE_ROLES, validators=[Required()]
    )
