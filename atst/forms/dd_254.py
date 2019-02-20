from wtforms.fields import SelectMultipleField, StringField
from wtforms.fields.html5 import TelField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Required

from atst.forms.validators import PhoneNumber

from .forms import CacheableForm
from .data import REQUIRED_DISTRIBUTIONS
from atst.utils.localization import translate


class DD254Form(CacheableForm):
    certifying_official = StringField(
        translate("forms.dd_254.certifying_official.label"),
        description=translate("forms.dd_254.certifying_official.description"),
        validators=[Required()],
    )
    certifying_official_title = StringField(
        translate("forms.dd_254.certifying_official_title.label"),
        validators=[Required()],
    )
    certifying_official_address = StringField(
        translate("forms.dd_254.certifying_official_address.label"),
        description=translate("forms.dd_254.certifying_official_address.description"),
        validators=[Required()],
    )
    certifying_official_phone = TelField(
        translate("forms.dd_254.certifying_official_phone.label"),
        description=translate("forms.dd_254.certifying_official_phone.description"),
        validators=[Required(), PhoneNumber()],
    )
    required_distribution = SelectMultipleField(
        translate("forms.dd_254.required_distribution.label"),
        choices=REQUIRED_DISTRIBUTIONS,
        default="",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
