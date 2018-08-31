from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length

from atst.forms.validators import IsNumber
from atst.forms.fields import SelectField

from .data import WORKSPACE_ROLES


class UpdateMemberForm(Form):

    workspace_role = SelectField(
        "Workspace Role", choices=WORKSPACE_ROLES, validators=[Required()], default=""
    )
