import re
import pendulum
from wtforms.fields.html5 import DateField, EmailField
from wtforms.fields import StringField, FileField, FormField
from wtforms.validators import InputRequired, Email, Regexp, Optional
from flask_wtf.file import FileAllowed
from werkzeug.datastructures import FileStorage

from .fields import NewlineListField, SelectField, NumberStringField
from atst.forms.forms import CacheableForm
from atst.utils.localization import translate
from .data import FUNDING_TYPES
from .validators import DateRange


TREASURY_CODE_REGEX = re.compile(r"^0*([1-9]{4}|[1-9]{6})$")

BA_CODE_REGEX = re.compile(r"[0-9]{2}\w?$")


def number_to_int(num):
    if num:
        return int(num)


def coerce_choice(val):
    if val is None:
        return None
    elif isinstance(val, str):
        return val
    else:
        return val.value


class TaskOrderForm(CacheableForm):
    def do_validate_number(self):
        for field in self:
            if field.name != "legacy_task_order-number":
                field.validators.insert(0, Optional())

        valid = super().validate()

        for field in self:
            if field.name != "legacy_task_order-number":
                field.validators.pop(0)

        return valid

    number = StringField(
        translate("forms.financial.number_label"),
        description=translate("forms.financial.number_description"),
        validators=[InputRequired()],
    )

    funding_type = SelectField(
        description=translate("forms.financial.funding_type_description"),
        choices=FUNDING_TYPES,
        validators=[InputRequired()],
        coerce=coerce_choice,
        render_kw={"required": False},
    )

    funding_type_other = StringField(
        translate("forms.financial.funding_type_other_label")
    )

    expiration_date = DateField(
        translate("forms.financial.expiration_date_label"),
        description=translate("forms.financial.expiration_date_description"),
        validators=[
            InputRequired(),
            DateRange(
                lower_bound=pendulum.duration(days=0),
                upper_bound=pendulum.duration(years=100),
                message="Must be a date in the future.",
            ),
        ],
        format="%m/%d/%Y",
    )

    clin_0001 = NumberStringField(
        translate("forms.financial.clin_0001_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_0001_description"),
        filters=[number_to_int],
    )

    clin_0003 = NumberStringField(
        translate("forms.financial.clin_0003_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_0003_description"),
        filters=[number_to_int],
    )

    clin_1001 = NumberStringField(
        translate("forms.financial.clin_1001_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_1001_description"),
        filters=[number_to_int],
    )

    clin_1003 = NumberStringField(
        translate("forms.financial.clin_1003_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_1003_description"),
        filters=[number_to_int],
    )

    clin_2001 = NumberStringField(
        translate("forms.financial.clin_2001_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_2001_description"),
        filters=[number_to_int],
    )

    clin_2003 = NumberStringField(
        translate("forms.financial.clin_2003_label"),
        validators=[InputRequired()],
        description=translate("forms.financial.clin_2003_description"),
        filters=[number_to_int],
    )

    pdf = FileField(
        translate("forms.financial.pdf_label"),
        validators=[
            FileAllowed(["pdf"], translate("forms.financial.pdf_allowed_description")),
            InputRequired(),
        ],
        render_kw={"required": False},
    )


class RequestFinancialVerificationForm(CacheableForm):
    uii_ids = NewlineListField(
        translate("forms.financial.uii_ids_label"),
        description=translate("forms.financial.uii_ids_description"),
    )

    pe_id = StringField(
        translate("forms.financial.pe_id_label"),
        description=translate("forms.financial.pe_id_description"),
        validators=[InputRequired()],
    )

    treasury_code = StringField(
        translate("forms.financial.treasury_code_label"),
        description=translate("forms.financial.treasury_code_description"),
        validators=[InputRequired(), Regexp(TREASURY_CODE_REGEX)],
    )

    ba_code = StringField(
        translate("forms.financial.ba_code_label"),
        description=translate("forms.financial.ba_code_description"),
        validators=[InputRequired(), Regexp(BA_CODE_REGEX)],
    )

    fname_co = StringField(
        translate("forms.financial.fname_co_label"), validators=[InputRequired()]
    )
    lname_co = StringField(
        translate("forms.financial.lname_co_label"), validators=[InputRequired()]
    )

    email_co = EmailField(
        translate("forms.financial.email_co_label"),
        validators=[InputRequired(), Email()],
    )

    office_co = StringField(
        translate("forms.financial.office_co_label"), validators=[InputRequired()]
    )

    fname_cor = StringField(
        translate("forms.financial.fname_cor_label"), validators=[InputRequired()]
    )

    lname_cor = StringField(
        translate("forms.financial.lname_cor_label"), validators=[InputRequired()]
    )

    email_cor = EmailField(
        translate("forms.financial.email_cor_label"),
        validators=[InputRequired(), Email()],
    )

    office_cor = StringField(
        translate("forms.financial.office_cor_label"), validators=[InputRequired()]
    )

    def reset(self):
        """
        Reset UII info so that it can be de-parsed rendered properly.
        This is a stupid workaround, and there's probably a better way.
        """
        self.uii_ids.process_data(self.uii_ids.data)


class FinancialVerificationForm(CacheableForm):

    legacy_task_order = FormField(TaskOrderForm)
    request = FormField(RequestFinancialVerificationForm)

    def validate(self, *args, **kwargs):
        if not kwargs.get("is_extended", True):
            return self.do_validate_request()

        if self.legacy_task_order.funding_type.data == "OTHER":
            self.legacy_task_order.funding_type_other.validators.append(InputRequired())

        to_pdf_validators = None
        if kwargs.get("has_attachment"):
            to_pdf_validators = list(self.legacy_task_order.pdf.validators)
            self.legacy_task_order.pdf.validators = []

        valid = super().validate()

        if to_pdf_validators:
            self.legacy_task_order.pdf.validators = to_pdf_validators

        return valid

    def do_validate_request(self):
        """
        Called do_validate_request to avoid being considered an inline
        validator by wtforms.
        """
        request_valid = self.request.validate(self)
        task_order_valid = self.legacy_task_order.do_validate_number()
        return request_valid and task_order_valid

    def reset(self):
        self.request.reset()

    @property
    def pe_id(self):
        return self.request.pe_id

    @property
    def has_pdf_upload(self):
        return isinstance(self.legacy_task_order.pdf.data, FileStorage)

    @property
    def is_missing_task_order_number(self):
        return "number" in self.errors.get("legacy_task_order", {})

    @property
    def is_only_missing_task_order_number(self):
        return "task_order_number" in self.errors and len(self.errors) == 1
