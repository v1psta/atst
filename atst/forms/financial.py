import tornado
from tornado.gen import Return
from wtforms.fields.html5 import EmailField
from wtforms.fields import StringField, SelectField
from wtforms.form import Form
from wtforms.validators import Required, Email

from .fields import NewlineListField
from .forms import ValidatedForm


@tornado.gen.coroutine
def validate_pe_id(field, existing_request, fundz_client):
    response = yield fundz_client.get(
        "/pe-number/{}".format(field.data),
        raise_error=False,
    )
    if not response.ok:
        field.errors.append(
            "We couldn't find that PE number, but if you have double checked "
            "it you can submit anyway. Your request will need to go through a "
            "manual review."
        )
        return False

    return True


class FinancialForm(ValidatedForm):

    @tornado.gen.coroutine
    def perform_extra_validation(self, existing_request, fundz_client):
        valid = True
        if not existing_request or existing_request.get('pe_id') != self.pe_id.data:
            valid = yield validate_pe_id(self.pe_id, existing_request, fundz_client)
        raise Return(valid)

    task_order_id = StringField(
        "Task Order Number associated with this request.", validators=[Required()]
    )

    uii_ids = NewlineListField(
        "Unique Item Identifier (UII)s related to your application(s) if you already have them."
    )

    pe_id = StringField(
        "Program Element (PE) Number related to your request"
    )

    treasury_code = StringField("Please provide your Program Treasury Code")

    ba_code = StringField("Please provide your Program BA Code")

    fname_co = StringField("Contracting Officer First Name", validators=[Required()])
    lname_co = StringField("Contracting Officer Last Name", validators=[Required()])

    email_co = EmailField("Contracting Officer Email", validators=[Required(), Email()])

    office_co = StringField("Contracting Office Office", validators=[Required()])

    fname_cor = StringField(
        "Contracting Officer Representative (COR) First Name", validators=[Required()]
    )

    lname_cor = StringField(
        "Contracting Officer Representative (COR) Last Name", validators=[Required()]
    )

    email_cor = EmailField(
        "Contracting Officer Representative (COR) Email",
        validators=[Required(), Email()],
    )

    office_cor = StringField(
        "Contracting Officer Representative (COR) Office", validators=[Required()]
    )

    funding_type = SelectField(
        validators=[Required()],
        choices=[
            ("", "- Select -"),
            ("RDTE", "Research, Development, Testing & Evaluation (RDT&E)"),
            ("OM", "Operations & Maintenance (O&M)"),
            ("PROC", "Procurement (PROC)"),
            ("OTHER", "Other"),
        ],
    )

    funding_type_other = StringField(
        "If other, please specify", validators=[Required()]
    )

    clin_0001 = StringField(
        "<dl><dt>CLIN 0001</dt> - <dd>Unclassified IaaS and PaaS Amount</dd></dl>", validators=[Required()]
    )

    clin_0003 = StringField(
        "<dl><dt>CLIN 0003</dt> - <dd>Unclassified Cloud Support Package</dd></dl>", validators=[Required()]
    )

    clin_1001 = StringField(
        "<dl><dt>CLIN 1001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
    )

    clin_1003 = StringField(
        "<dl><dt>CLIN 1003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 1</dd></dl>",
        validators=[Required()],
    )

    clin_2001 = StringField(
        "<dl><dt>CLIN 2001</dt> - <dd>Unclassified IaaS and PaaS Amount <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
    )

    clin_2003 = StringField(
        "<dl><dt>CLIN 2003</dt> - <dd>Unclassified Cloud Support Package <br> OPTION PERIOD 2</dd></dl>",
        validators=[Required()],
    )
