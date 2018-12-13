from wtforms.fields import StringField

from .forms import CacheableForm


class TaskOrderForm(CacheableForm):
    clin_0001 = StringField("CLIN 0001")
    clin_0003 = StringField("CLIN 0003")
    clin_1001 = StringField("CLIN 1001")
    clin_1003 = StringField("CLIN 1003")
    clin_2001 = StringField("CLIN 2001")
    clin_2003 = StringField("CLIN 2003")
