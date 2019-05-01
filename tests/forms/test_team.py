from wtforms.validators import ValidationError
import pytest

from atst.domain.permission_sets import PermissionSets
from atst.forms.team import *


def test_permissions_form_permission_sets():
    form_data = {
        "perms_env_mgmt": "",
        "perms_team_mgmt": PermissionSets.EDIT_APPLICATION_TEAM,
        "perms_del_env": "",
    }
    form = PermissionsForm(data=form_data)
    assert form.validate()
    assert form.data == [PermissionSets.EDIT_APPLICATION_TEAM]


def test_permissions_form_invalid():
    form_data = {
        "perms_env_mgmt": "not a real choice",
        "perms_team_mgmt": PermissionSets.EDIT_APPLICATION_TEAM,
        "perms_del_env": "",
    }
    form = PermissionsForm(data=form_data)
    assert not form.validate()
