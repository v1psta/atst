import pytest
from atst.domain.permission_sets import PermissionSets
from atst.domain.exceptions import NotFoundError


def test_get_all_roles():
    roles = PermissionSets.get_all()
    assert roles


def test_get_existing_role():
    role = PermissionSets.get("developer")
    assert role.name == "developer"


def test_get_nonexistent_role():
    with pytest.raises(NotFoundError):
        PermissionSets.get("nonexistent")
