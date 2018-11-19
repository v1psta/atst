from wtforms.fields import StringField
from wtforms.validators import Length

from .forms import CacheableForm


class WorkspaceForm(CacheableForm):
    name = StringField(
        "Workspace Name",
        validators=[
            Length(
                min=4,
                max=100,
                message="Workspace names must be at least 4 and not more than 50 characters",
            )
        ],
    )
