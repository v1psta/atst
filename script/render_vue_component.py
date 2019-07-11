from jinja2 import Environment, FileSystemLoader
from wtforms.widgets import CheckboxInput
from wtforms.fields import BooleanField
from wtforms import Form

env = Environment(loader=FileSystemLoader('templates/components'))

checkbox_template = env.get_template('checkbox_input.html')

field = BooleanField(
    label="Hooray!",
    default=False,
    widget=CheckboxInput()
)

class BoolForm(Form):
    testVal = field

ci_macro = getattr(checkbox_template.module, 'CheckboxInput')

output_from_parsed_template = ci_macro(BoolForm().testVal)
print(output_from_parsed_template)

with open("js/test_templates/checkbox_input_template.html", "w") as fh:
    fh.write(output_from_parsed_template)
