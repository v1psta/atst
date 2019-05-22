from wtforms.validators import ValidationError

from atst.domain.permission_sets import PermissionSets
from atst.forms.team import *


def test_permissions_form_permission_sets():
    form_data = {
        "perms_team_mgmt": PermissionSets.EDIT_APPLICATION_TEAM,
        "perms_env_mgmt": PermissionSets.VIEW_APPLICATION,
        "perms_del_env": PermissionSets.VIEW_APPLICATION,
    }
    form = PermissionsForm(data=form_data)

    assert form.validate()
    assert form.data == [
        PermissionSets.EDIT_APPLICATION_TEAM,
        PermissionSets.VIEW_APPLICATION,
        PermissionSets.VIEW_APPLICATION,
    ]


def test_permissions_form_invalid():
    form_data = {
        "perms_team_mgmt": PermissionSets.EDIT_APPLICATION_TEAM,
        "perms_env_mgmt": "not a real choice",
        "perms_del_env": PermissionSets.VIEW_APPLICATION,
    }
    form = PermissionsForm(data=form_data)
    assert not form.validate()
