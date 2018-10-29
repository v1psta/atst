import re
import pendulum
from wtforms.fields.html5 import DateField, EmailField
from wtforms.fields import StringField, FileField, FormField
from wtforms.validators import InputRequired, Email, Regexp, Optional
from flask_wtf.file import FileAllowed

from .fields import NewlineListField, SelectField, NumberStringField
from atst.forms.forms import ValidatedForm
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


class DraftValidateMixin(object):
    def validate_draft(self):
        """
        Make all fields optional before validation, and then return them to
        their previous state.
        """
        for field in self:
            field.validators.insert(0, Optional())

        valid = self.validate()

        for field in self:
            field.validators.pop(0)

        return valid


class TaskOrderForm(ValidatedForm, DraftValidateMixin):
    def do_validate_number(self):
        for field in self:
            if field.name != "task_order-number":
                field.validators.insert(0, Optional())

        valid = super().validate()

        for field in self:
            if field.name != "task_order-number":
                field.validators.pop(0)

        return valid

    number = StringField(
        "Task Order Number associated with this request",
        description="Include the original Task Order number (including the 000X at the end). Do not include any modification numbers. Note that there may be a lag between approving a task order and when it becomes available in our system.",
        validators=[InputRequired()],
    )

    funding_type = SelectField(
        description="What is the source of funding?",
        choices=FUNDING_TYPES,
        validators=[InputRequired()],
        coerce=coerce_choice,
        render_kw={"required": False},
    )

    funding_type_other = StringField("If other, please specify")

    expiration_date = DateField(
        "Task Order Expiration Date",
        description="Please enter the expiration date for the Task Order",
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
        "<dl><dt>CLIN 0001</dt> - <dd>Unclassified IaaS and PaaS Amount</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    clin_0003 = NumberStringField(
        "<dl><dt>CLIN 0003</dt> - <dd>Unclassified Cloud Support Package</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    clin_1001 = NumberStringField(
        "<dl><dt>CLIN 1001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 1</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    clin_1003 = NumberStringField(
        "<dl><dt>CLIN 1003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 1</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    clin_2001 = NumberStringField(
        "<dl><dt>CLIN 2001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 2</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    clin_2003 = NumberStringField(
        "<dl><dt>CLIN 2003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 2</dd></dl>",
        validators=[InputRequired()],
        description="Review your task order document, the amounts for each CLIN must match exactly here",
        filters=[number_to_int],
    )

    pdf = FileField(
        "Upload a copy of your Task Order",
        validators=[
            FileAllowed(["pdf"], "Only PDF documents can be uploaded."),
            InputRequired(),
        ],
        render_kw={"required": False},
    )


class RequestFinancialVerificationForm(ValidatedForm, DraftValidateMixin):
    uii_ids = NewlineListField(
        "Unique Item Identifier (UII)s related to your application(s) if you already have them.",
        description="If you have more than one UII, place each one on a new line.",
    )

    pe_id = StringField(
        "Program Element Number",
        description="PE numbers help the Department of Defense identify which offices' budgets are contributing towards this resource use. <br/><em>It should be 7 digits followed by 1-3 letters, and should have a zero as the first and third digits.</em>",
        validators=[InputRequired()],
    )

    treasury_code = StringField(
        "Program Treasury Code",
        description="Program Treasury Code (or Appropriations Code) identifies resource types. <br/> <em>It should be a four digit or six digit number, optionally prefixed by one or more zeros.</em>",
        validators=[InputRequired(), Regexp(TREASURY_CODE_REGEX)],
    )

    ba_code = StringField(
        "Program Budget Activity (BA) Code",
        description="BA Code is used to identify the purposes, projects, or types of activities financed by the appropriation fund. <br/><em>It should be two digits, followed by an optional letter.</em>",
        validators=[InputRequired(), Regexp(BA_CODE_REGEX)],
    )

    fname_co = StringField("KO First Name", validators=[InputRequired()])
    lname_co = StringField("KO Last Name", validators=[InputRequired()])

    email_co = EmailField("KO Email", validators=[InputRequired(), Email()])

    office_co = StringField("KO Office", validators=[InputRequired()])

    fname_cor = StringField("COR First Name", validators=[InputRequired()])

    lname_cor = StringField("COR Last Name", validators=[InputRequired()])

    email_cor = EmailField("COR Email", validators=[InputRequired(), Email()])

    office_cor = StringField("COR Office", validators=[InputRequired()])

    def reset(self):
        """
        Reset UII info so that it can be de-parsed rendered properly.
        This is a stupid workaround, and there's probably a better way.
        """
        self.uii_ids.process_data(self.uii_ids.data)


class FinancialVerificationForm(ValidatedForm):

    task_order = FormField(TaskOrderForm)
    request = FormField(RequestFinancialVerificationForm)

    def validate(self, *args, **kwargs):
        if not kwargs.get("is_extended", True):
            return self.do_validate_request()

        if self.task_order.funding_type.data == "OTHER":
            self.task_order.funding_type_other.validators.append(InputRequired())

        to_pdf_validators = None
        if kwargs.get("has_attachment"):
            to_pdf_validators = list(self.task_order.pdf.validators)
            self.task_order.pdf.validators = []

        valid = super().validate()

        if to_pdf_validators:
            self.task_order.pdf.validators = to_pdf_validators

        return valid

    def do_validate_request(self):
        """
        Called do_validate_request to avoid being considered an inline
        validator by wtforms.
        """
        request_valid = self.request.validate(self)
        task_order_valid = self.task_order.do_validate_number()
        return request_valid and task_order_valid

    def validate_draft(self):
        return self.task_order.validate_draft() and self.request.validate_draft()

    def reset(self):
        self.request.reset()

    @property
    def pe_id(self):
        return self.request.pe_id

    @property
    def task_order_number(self):
        return self.task_order.number

    @property
    def is_missing_task_order_number(self):
        return "number" in self.errors.get("task_order", {})

    @property
    def is_only_missing_task_order_number(self):
        return "task_order_number" in self.errors and len(self.errors) == 1
