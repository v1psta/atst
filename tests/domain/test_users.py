import pytest
from uuid import uuid4

from atst.domain.users import Users
from atst.domain.exceptions import NotFoundError



def test_create_user():
    user = Users.create("developer")
    assert user.atat_role.name == "developer"


def test_create_user_with_nonexistent_role():
    with pytest.raises(NotFoundError):
        Users.create("nonexistent")


def test_get_or_create_nonexistent_user():
    user_id = uuid4()
    user = Users.get_or_create(user_id, atat_role_name="developer")
    assert user.id == user_id


def test_get_or_create_existing_user():
    user_id = uuid4()
    Users.get_or_create(user_id, atat_role_name="developer")
    user = Users.get_or_create(user_id, atat_role_name="developer")
    assert user


def test_get_user():
    new_user = Users.create("developer")
    user = Users.get(new_user.id)
    assert user.id == new_user.id


def test_get_nonexistent_user():
    Users.create("developer")
    with pytest.raises(NotFoundError):
        Users.get(uuid4())


def test_get_user_by_dod_id():
    new_user = Users.create("developer", dod_id="my_dod_id")
    user = Users.get_by_dod_id("my_dod_id")
    assert user == new_user


def test_update_user():
    new_user = Users.create("developer")
    updated_user = Users.update(new_user.id, "ccpo")

    assert updated_user.atat_role.name == "ccpo"


def test_update_nonexistent_user():
    Users.create("developer")
    with pytest.raises(NotFoundError):
        Users.update(uuid4(), "ccpo")


def test_update_existing_user_with_nonexistent_role():
    new_user = Users.create("developer")
    with pytest.raises(NotFoundError):
        Users.update(new_user.id, "nonexistent")
