from wtforms.fields import (
    BooleanField,
    DecimalField,
    FieldList,
    FormField,
    StringField,
    HiddenField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Optional
from flask_wtf import FlaskForm

from .data import JEDI_CLIN_TYPES
from .fields import SelectField
from .forms import BaseForm
from atst.utils.localization import translate


def coerce_enum(enum_inst):
    if getattr(enum_inst, "value", None):
        return enum_inst.value
    else:
        return enum_inst


class CLINForm(FlaskForm):
    jedi_clin_type = SelectField(
        translate("task_orders.form.clin_type_label"),
        choices=JEDI_CLIN_TYPES,
        coerce=coerce_enum,
    )

    number = StringField(
        label=translate("task_orders.form.clin_number_label"), validators=[Optional()]
    )
    start_date = DateField(
        translate("forms.task_order.start_date_label"),
        format="%m/%d/%Y",
        validators=[Optional()],
    )
    end_date = DateField(
        translate("forms.task_order.end_date_label"),
        format="%m/%d/%Y",
        validators=[Optional()],
    )
    obligated_amount = DecimalField(
        label=translate("task_orders.form.obligated_funds_label"),
        validators=[Optional()],
    )
    loas = FieldList(StringField())

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)
        if self.start_date.data > self.end_date.data:
            self.start_date.errors.append(
                translate("forms.task_order.start_date_error")
            )
            return False
        else:
            return valid


class AttachmentForm(BaseForm):
    filename = HiddenField(id="attachment_filename")
    object_name = HiddenField(id="attachment_object_name")
    accept = ".pdf,application/pdf"


class TaskOrderForm(BaseForm):
    number = StringField(label=translate("forms.task_order.number_description"))
    pdf = FormField(
        AttachmentForm,
        label=translate("task_orders.form.supporting_docs_size_limit"),
        description=translate("task_orders.form.supporting_docs_size_limit"),
    )
    clins = FieldList(FormField(CLINForm))


class SignatureForm(BaseForm):
    signature = BooleanField(
        translate("task_orders.sign.digital_signature_description"),
        validators=[Required()],
    )
