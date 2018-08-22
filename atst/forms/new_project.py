from flask_wtf import Form
from wtforms.fields import StringField, TextAreaField, FieldList
from wtforms.validators import Required
from atst.forms.validators import ListItemRequired


class NewProjectForm(Form):

    EMPTY_ENVIRONMENT_NAMES = ["", None]

    name = StringField(label="Project Name", validators=[Required()])
    description = TextAreaField(label="Description", validators=[Required()])
    environment_names = FieldList(
        StringField(label="Environment Name"),
        validators=[ListItemRequired(message="Provide at least one environment name.")],
    )

    @property
    def data(self):
        _data = super(Form, self).data
        _data["environment_names"] = [n for n in _data["environment_names"] if n not in self.EMPTY_ENVIRONMENT_NAMES]
        return _data
