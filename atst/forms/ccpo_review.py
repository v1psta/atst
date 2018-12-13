from wtforms.fields.html5 import EmailField, TelField
from wtforms.fields import StringField, TextAreaField
from wtforms.validators import Email, Optional

from .forms import CacheableForm
from .validators import Name, PhoneNumber

from atst.utils.localization import translate


class CCPOReviewForm(CacheableForm):
    comment = TextAreaField(
        translate("forms.ccpo_review.comment_label"),
        description=("forms.ccpo_review.comment_description"),
    )
    fname_mao = StringField(
        translate("forms.ccpo_review.fname_mao_label"), validators=[Optional(), Name()]
    )
    lname_mao = StringField(
        translate("forms.ccpo_review.lname_mao_label"), validators=[Optional(), Name()]
    )
    email_mao = EmailField(
        translate("forms.ccpo_review.email_mao_label"), validators=[Optional(), Email()]
    )
    phone_mao = TelField(
        translate("forms.ccpo_review.phone_mao_label"),
        validators=[Optional(), PhoneNumber()],
    )
    phone_ext_mao = StringField(translate("forms.ccpo_review.phone_ext_mao_label"))
    fname_ccpo = StringField(
        translate("forms.ccpo_review.fname_ccpo_label"), validators=[Optional(), Name()]
    )
    lname_ccpo = StringField(
        translate("forms.ccpo_review.lname_ccpo_label"), validators=[Optional(), Name()]
    )
