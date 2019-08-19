from wtforms.validators import ValidationError

from atst.forms.data import ENV_ROLES, ENV_ROLE_NO_ACCESS as NO_ACCESS
from atst.forms.application_member import *


def test_environment_form():
    form_data = {
        "environment_id": 123,
        "environment_name": "testing",
        "role": ENV_ROLES[0][0],
    }
    form = EnvironmentForm(data=form_data)
    assert form.validate()


def test_environment_form_default_no_access():
    form_data = {"environment_id": 123, "environment_name": "testing"}
    form = EnvironmentForm(data=form_data)

    assert form.validate()
    assert form.data == {
        "environment_id": 123,
        "environment_name": "testing",
        "role": None,
    }


def test_environment_form_invalid():
    form_data = {
        "environment_id": 123,
        "environment_name": "testing",
        "role": "not a real choice",
    }
    form = EnvironmentForm(data=form_data)
    assert not form.validate()
