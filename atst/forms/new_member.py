from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length

from atst.forms.validators import IsNumber
from atst.forms.fields import SelectField
from atst.utils.localization import translate

from .data import WORKSPACE_ROLES


class NewMemberForm(FlaskForm):

    first_name = StringField(
        label=translate("forms.new_member.first_name_label"), validators=[Required()]
    )
    last_name = StringField(
        label=translate("forms.new_member.last_name_label"), validators=[Required()]
    )
    email = EmailField(
        translate("forms.new_member.email_label"), validators=[Required(), Email()]
    )
    dod_id = StringField(
        translate("forms.new_member.dod_id_label"),
        validators=[Required(), Length(min=10), IsNumber()],
    )
    workspace_role = SelectField(
        translate("forms.new_member.workspace_role_label"),
        choices=WORKSPACE_ROLES,
        validators=[Required()],
        default="",
        description=translate("forms.new_member.workspace_role_description"),
    )
