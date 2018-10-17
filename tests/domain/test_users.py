import pytest
from uuid import uuid4

from atst.domain.users import Users
from atst.domain.exceptions import NotFoundError, AlreadyExistsError, UnauthorizedError

DOD_ID = "my_dod_id"


def test_create_user():
    user = Users.create(DOD_ID, "developer")
    assert user.atat_role.name == "developer"


def test_create_user_with_existing_email():
    Users.create(DOD_ID, "developer", email="thisusersemail@usersRus.com")
    with pytest.raises(AlreadyExistsError):
        Users.create(DOD_ID, "admin", email="thisusersemail@usersRus.com")


def test_create_user_with_nonexistent_role():
    with pytest.raises(NotFoundError):
        Users.create(DOD_ID, "nonexistent")


def test_get_or_create_nonexistent_user():
    user = Users.get_or_create_by_dod_id(DOD_ID, atat_role_name="developer")
    assert user.dod_id == DOD_ID


def test_get_or_create_existing_user():
    Users.get_or_create_by_dod_id(DOD_ID, atat_role_name="developer")
    user = Users.get_or_create_by_dod_id(DOD_ID, atat_role_name="developer")
    assert user


def test_get_user():
    new_user = Users.create(DOD_ID, "developer")
    user = Users.get(new_user.id)
    assert user.id == new_user.id


def test_get_nonexistent_user():
    Users.create(DOD_ID, "developer")
    with pytest.raises(NotFoundError):
        Users.get(uuid4())


def test_get_user_by_dod_id():
    new_user = Users.create(DOD_ID, "developer")
    user = Users.get_by_dod_id(DOD_ID)
    assert user == new_user


def test_update_role():
    new_user = Users.create(DOD_ID, "developer")
    updated_user = Users.update_role(new_user.id, "ccpo")

    assert updated_user.atat_role.name == "ccpo"


def test_update_role_with_nonexistent_user():
    Users.create(DOD_ID, "developer")
    with pytest.raises(NotFoundError):
        Users.update_role(uuid4(), "ccpo")


def test_update_existing_user_with_nonexistent_role():
    new_user = Users.create(DOD_ID, "developer")
    with pytest.raises(NotFoundError):
        Users.update_role(new_user.id, "nonexistent")


def test_update_user():
    new_user = Users.create(DOD_ID, "developer")
    updated_user = Users.update(new_user, {"first_name": "Jabba"})
    assert updated_user.first_name == "Jabba"


def test_update_user_with_dod_id():
    new_user = Users.create(DOD_ID, "developer")
    with pytest.raises(UnauthorizedError) as excinfo:
        Users.update(new_user, {"dod_id": "1234567890"})

    assert "dod_id" in str(excinfo.value)
