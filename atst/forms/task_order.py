from wtforms.fields import BooleanField, DecimalField, FieldList, FileField, FormField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, Optional
from flask_wtf.file import FileAllowed

from .data import JEDI_CLIN_TYPES
from .fields import SelectField
from .forms import BaseForm
from atst.forms.validators import FileLength
from atst.utils.localization import translate


class CLINForm(FlaskForm):
    jedi_clin_type = SelectField("Jedi CLIN type", choices=JEDI_CLIN_TYPES)
    clin_number = StringField(validators=[Required()])
    start_date = DateField(
        translate("forms.task_order.start_date_label"),
        format="%m/%d/%Y",
        validators=[Required()],
    )
    end_date = DateField(
        translate("forms.task_order.end_date_label"),
        format="%m/%d/%Y",
        validators=[Required()],
    )
    obligated_funds = DecimalField()
    loas = FieldList(StringField())


class UnclassifiedCLINForm(CLINForm):
    # TODO: overwrite jedi_clin_type to only include the unclassified options
    pass


class TaskOrderForm(BaseForm):
    number = StringField(
        translate("forms.task_order.number_label"),
        description=translate("forms.task_order.number_description"),
        validators=[Required()],
    )
    pdf = FileField(
        None,
        validators=[
            FileAllowed(["pdf"], translate("forms.task_order.file_format_not_allowed")),
            FileLength(message=translate("forms.validators.file_length")),
        ],
        render_kw={"accept": ".pdf,application/pdf"},
    )
    clins = FieldList(FormField(CLINForm))


class SignatureForm(BaseForm):
    signature = BooleanField(
        translate("task_orders.sign.digital_signature_label"),
        description=translate("task_orders.sign.digital_signature_description"),
        validators=[Required()],
    )
