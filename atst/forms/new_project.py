from flask_wtf import Form
from wtforms.fields import StringField, TextAreaField, FieldList


class NewProjectForm(Form):

    name = StringField(label="Project Name")
    description = TextAreaField(label="Description")
    environment_name = StringField(label="Environment Name")
