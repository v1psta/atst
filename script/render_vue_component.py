import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from jinja2 import Environment, FileSystemLoader
from wtforms.widgets import CheckboxInput, FileInput
from wtforms.fields import StringField, FileField
from wtforms.validators import InputRequired
from wtforms import Form

from atst.filters import iconSvg

env = Environment(loader=FileSystemLoader('templates'))

env.filters['iconSvg'] = iconSvg

# override tojson as identity function to prevent
# wrapping strings in extra quotes
env.filters['tojson'] = lambda x: x

class InitialValueForm(Form):
    datafield = StringField(
        label="initialvalue value",
        default="initialvalue"
    )

    errorfield = StringField(
        label="error",
        validators=[InputRequired(message="Test Error Message")]
    )

checkbox_template = env.get_template('components/checkbox_input.html')
ci_macro = getattr(checkbox_template.module, 'CheckboxInput')
checkbox_input_form = InitialValueForm()
checkbox_input_form.datafield.widget = CheckboxInput()
rendered_checkbox_macro = ci_macro(checkbox_input_form.datafield)
with open("js/test_templates/checkbox_input_template.html", "w") as fh:
    fh.write(rendered_checkbox_macro)

upload_template = env.get_template('components/upload_input.html')
up_macro = getattr(upload_template.module, 'UploadInput')
rendered_upload_macro = up_macro(InitialValueForm().datafield)
with open("js/test_templates/upload_input_template.html", "w") as fh:
    fh.write(rendered_upload_macro)

erroredform = InitialValueForm()
erroredform.validate()
rendered_upload_error_macro = up_macro(erroredform.errorfield)
with open("js/test_templates/upload_input_error_template.html", "w") as fh:
    fh.write(rendered_upload_error_macro)
