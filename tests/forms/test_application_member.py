from wtforms.validators import ValidationError

from atst.domain.permission_sets import PermissionSets
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


def test_update_member_form():
    form_data = {
        "member_role_id": 123,
        "permission_sets": {
            "perms_team_mgmt": True,
            "perms_env_mgmt": False,
            "perms_del_env": False,
        },
        "environment_roles": {
            "environment_id": 123,
            "environment_name": "testing",
            "role": ENV_ROLES[0][0],
        },
    }
    form = UpdateMemberForm(data=form_data)
    assert form.validate()
