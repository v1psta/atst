import pytest

from wtforms.widgets import CheckboxInput
from wtforms.fields import StringField
from wtforms.validators import InputRequired, URL
from wtforms import Form, FormField


class InitialValueForm(Form):
    datafield = StringField(label="initialvalue value", default="initialvalue")

    errorfield = StringField(
        label="error", validators=[InputRequired(message="Test Error Message")]
    )


class TaskOrderPdfForm(Form):
    filename = StringField(default="initialvalue")
    object_name = StringField()

    errorfield = StringField(
        label="error", validators=[InputRequired(message="Test Error Message")]
    )


class TaskOrderForm(Form):
    pdf = FormField(TaskOrderPdfForm, label="task_order_pdf")


@pytest.fixture
def env(app, scope="function"):
    return app.jinja_env


@pytest.fixture
def upload_input_macro(env):
    # override tojson as identity function to prevent
    # wrapping strings in extra quotes
    env.filters["tojson"] = lambda x: x
    upload_template = env.get_template("components/upload_input.html")
    return getattr(upload_template.module, "UploadInput")


@pytest.fixture
def checkbox_input_macro(env):
    checkbox_template = env.get_template("components/checkbox_input.html")
    return getattr(checkbox_template.module, "CheckboxInput")


@pytest.fixture
def initial_value_form(scope="function"):
    return InitialValueForm()


@pytest.fixture
def task_order_form(scope="function"):
    return TaskOrderForm()


@pytest.fixture
def error_task_order_form(scope="function"):
    return ErrorTaskOrderForm()


def write_template(content, name):
    with open("js/test_templates/{}".format(name), "w") as fh:
        fh.write(content)


def test_make_checkbox_input_template(checkbox_input_macro, initial_value_form):
    initial_value_form.datafield.widget = CheckboxInput()
    rendered_checkbox_macro = checkbox_input_macro(initial_value_form.datafield)
    write_template(rendered_checkbox_macro, "checkbox_input_template.html")


def test_make_upload_input_template(upload_input_macro, task_order_form):
    rendered_upload_macro = upload_input_macro(
        task_order_form.pdf, token="token", object_name="object_name"
    )
    write_template(rendered_upload_macro, "upload_input_template.html")


def test_make_upload_input_error_template(upload_input_macro, task_order_form):
    task_order_form.validate()
    rendered_upload_macro = upload_input_macro(
        task_order_form.pdf, token="token", object_name="object_name"
    )
    write_template(rendered_upload_macro, "upload_input_error_template.html")
