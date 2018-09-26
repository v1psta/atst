from flask_wtf import FlaskForm
from wtforms.fields import StringField, TextAreaField, FieldList
from wtforms.validators import Required
from atst.forms.validators import ListItemRequired, ListItemsUnique


class NewProjectForm(FlaskForm):

    EMPTY_ENVIRONMENT_NAMES = ["", None]

    name = StringField(label="Project Name", validators=[Required()])
    description = TextAreaField(label="Description", validators=[Required()])
    environment_names = FieldList(
        StringField(label="Environment Name"),
        validators=[
            ListItemRequired(message="Provide at least one environment name."),
            ListItemsUnique(message="Environment names must be unique."),
        ],
    )

    @property
    def data(self):
        _data = super(FlaskForm, self).data
        _data["environment_names"] = [
            n
            for n in _data["environment_names"]
            if n not in self.EMPTY_ENVIRONMENT_NAMES
        ]
        return _data
