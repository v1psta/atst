from wtforms.fields import BooleanField

from .forms import ValidatedForm


class ReviewForm(ValidatedForm):
    reviewed = BooleanField("I have reviewed this data and it is correct.")
