from wtforms.fields import (
    BooleanField,
    StringField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Optional

from .forms import BaseForm
from atst.utils.localization import translate


class TaskOrderForm(BaseForm):
    number = StringField(validators=[Required()])


class FundingForm(BaseForm):
    start_date = DateField(
        translate("forms.task_order.start_date_label"), format="%m/%d/%Y"
    )
    end_date = DateField(
        translate("forms.task_order.end_date_label"), format="%m/%d/%Y"
    )
    clin_01 = DecimalField(
        translate("forms.task_order.clin_01_label"), validators=[Optional()]
    )
    clin_02 = DecimalField(
        translate("forms.task_order.clin_02_label"), validators=[Optional()]
    )
    clin_03 = DecimalField(
        translate("forms.task_order.clin_03_label"), validators=[Optional()]
    )
    clin_04 = DecimalField(
        translate("forms.task_order.clin_04_label"), validators=[Optional()]
    )


class UnclassifiedFundingForm(FundingForm):
    clin_02 = StringField(
        translate("forms.task_order.unclassified_clin_02_label"),
        filters=[BaseForm.remove_empty_string],
    )
    clin_04 = StringField(
        translate("forms.task_order.unclassified_clin_04_label"),
        filters=[BaseForm.remove_empty_string],
    )


class SignatureForm(BaseForm):
    signature = BooleanField(
        translate("task_orders.sign.digital_signature_label"),
        description=translate("task_orders.sign.digital_signature_description"),
        validators=[Required()],
    )
