from wtforms.fields import (
    BooleanField,
    DecimalField,
    FieldList,
    FormField,
    StringField,
    HiddenField,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Optional, Length
from flask_wtf import FlaskForm
from datetime import datetime

from .data import JEDI_CLIN_TYPES
from .fields import SelectField
from .forms import BaseForm
from atst.utils.localization import translate
from flask import current_app as app


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
        translate("task_orders.form.pop_start"),
        description=translate("task_orders.form.pop_example"),
        format="%m/%d/%Y",
        validators=[Optional()],
    )
    end_date = DateField(
        translate("task_orders.form.pop_end"),
        description=translate("task_orders.form.pop_example"),
        format="%m/%d/%Y",
        validators=[Optional()],
    )
    total_amount = DecimalField(
        label=translate("task_orders.form.total_funds_label"),
        validators=[Optional()],
    )
    obligated_amount = DecimalField(
        label=translate("task_orders.form.obligated_funds_label"),
        validators=[Optional()],
    )

    def validate(self, *args, **kwargs):
        valid = super().validate(*args, **kwargs)
        contract_start = datetime.strptime(
            app.config.get("CONTRACT_START_DATE"), "%Y-%m-%d"
        ).date()
        contract_end = datetime.strptime(
            app.config.get("CONTRACT_END_DATE"), "%Y-%m-%d"
        ).date()

        if (
            self.start_date.data
            and self.end_date.data
            and self.start_date.data > self.end_date.data
        ):
            self.start_date.errors.append(
                translate("forms.task_order.pop_errors.date_order")
            )
            valid = False

        if self.start_date.data and self.start_date.data <= contract_start:
            self.start_date.errors.append(
                translate(
                    "forms.task_order.pop_errors.start",
                    {"date": contract_start.strftime("%b %d, %Y")},
                )
            )
            valid = False

        if self.end_date.data and self.end_date.data >= contract_end:
            self.end_date.errors.append(
                translate(
                    "forms.task_order.pop_errors.end",
                    {"date": contract_end.strftime("%b %d, %Y")},
                )
            )
            valid = False

        return valid


class AttachmentForm(BaseForm):
    filename = HiddenField(
        id="attachment_filename",
        validators=[
            Length(max=100, message=translate("forms.attachment.filename.length_error"))
        ],
    )
    object_name = HiddenField(
        id="attachment_object_name",
        validators=[
            Length(
                max=40, message=translate("forms.attachment.object_name.length_error")
            )
        ],
    )
    accept = ".pdf,application/pdf"

    def validate(self, *args, **kwargs):
        return super().validate(*args, **{**kwargs, "flash_invalid": False})


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
