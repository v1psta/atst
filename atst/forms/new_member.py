from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length

from .forms import BaseForm
from atst.forms.validators import IsNumber
from atst.forms.fields import SelectField
from atst.utils.localization import translate

from .data import PORTFOLIO_ROLES


class NewMemberForm(BaseForm):

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
    portfolio_role = SelectField(
        translate("forms.new_member.portfolio_role_label"),
        choices=PORTFOLIO_ROLES,
        validators=[Required()],
        default="",
        description=translate("forms.new_member.portfolio_role_description"),
    )
