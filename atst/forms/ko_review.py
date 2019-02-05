import pendulum
from flask_wtf.file import FileAllowed

from wtforms.fields.html5 import DateField
from wtforms.fields import StringField, TextAreaField, FileField
from wtforms.validators import Optional, Length

from .forms import CacheableForm
from .validators import IsNumber, DateRange

from atst.utils.localization import translate


class KOReviewForm(CacheableForm):
    start_date = DateField(
        translate("forms.ko_review.start_date_label"),
        format="%m/%d/%Y",
    )
    end_date = DateField(
        translate("forms.ko_review.end_date_label"),
        format="%m/%d/%Y",
    )
    pdf = FileField(
        translate("forms.ko_review.pdf_label"),
        description=translate("forms.ko_review.pdf_description"),
        validators=[
            FileAllowed(["pdf"], translate("forms.task_order.file_format_not_allowed"))
        ],
        render_kw={"required": False, "accept": ".pdf,application/pdf"},
    )
    number = StringField(
        translate("forms.ko_review.to_number"), validators=[Length(min=10)]
    )
    loa = StringField(
        translate("forms.ko_review.loa"), validators=[Length(min=10), IsNumber()]
    )
    custom_clauses = TextAreaField(
        translate("forms.ko_review.custom_clauses_label"),
        description=translate("forms.ko_review.custom_clauses_description"),
        validators=[Optional()],
    )
