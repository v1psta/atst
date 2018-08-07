import pytest
from atst.domain.roles import Roles
from atst.domain.exceptions import NotFoundError


def test_get_all_roles():
    roles = Roles.get_all()
    assert roles


def test_get_existing_role():
    role = Roles.get("developer")
    assert role.name == "developer"


def test_get_nonexistent_role():
    with pytest.raises(NotFoundError):
        Roles.get("nonexistent")
