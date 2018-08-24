from flask_wtf import Form
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, Length

from atst.forms.validators import IsNumber
from atst.forms.fields import SelectField


class NewMemberForm(Form):

    first_name = StringField(label="First Name", validators=[Required()])
    last_name = StringField(label="Last Name", validators=[Required()])
    email = EmailField("Email Address", validators=[Required(), Email()])
    dod_id = StringField("DOD ID", validators=[Required(), Length(min=10), IsNumber()])
    workspace_role = SelectField(
        "Workspace Role",
        choices=[
            ("", "Select a Role"),
            ("admin", "Admin"),
            ("billing_auditor", "Billing Auditor"),
            ("ccpo", "CCPO"),
            ("developer", "Developer"),
            ("owner", "Owner"),
            ("security_auditor", "Security Auditor"),
        ],
        validators=[Required()],
    )
