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

    perms_app_mgmt = SelectField(
        None,
        choices=[
            ("view_portfolio_application_management", "View Only"),
            ("edit_portfolio_application_management", "Edit Access"),
        ],
    )
    perms_funding = SelectField(
        None,
        choices=[
            ("view_portfolio_funding", "View Only"),
            ("edit_portfolio_funding", "Edit Access"),
        ],
    )
    perms_reporting = SelectField(
        None,
        choices=[
            ("view_portfolio_reports", "View Only"),
            ("edit_portfolio_reports", "Edit Access"),
        ],
    )
    perms_portfolio_mgmt = SelectField(
        None,
        choices=[
            ("view_portfolio_admin", "View Only"),
            ("edit_portfolio_admin", "Edit Access"),
        ],
    )

    @property
    def data(self):
        _data = super().data
        _data["permission_sets"] = []
        for field in _data:
            if "perms" in field:
                _data["permission_sets"].append(_data[field])

        return _data
