import pytest
from uuid import uuid4

from atst.domain.users import Users
from atst.domain.exceptions import NotFoundError, AlreadyExistsError


@pytest.fixture(scope="function")
def user_id():
    return uuid4()


def test_create_user(user_id):
    user = Users.create(user_id, "developer")
    assert user.id == user_id


def test_create_user_with_nonexistent_role(user_id):
    with pytest.raises(NotFoundError):
        Users.create(user_id, "nonexistent")


def test_create_already_existing_user(user_id):
    Users.create(user_id, "developer")
    with pytest.raises(AlreadyExistsError):
        Users.create(user_id, "developer")


def test_get_or_create_nonexistent_user(user_id):
    user = Users.get_or_create(user_id, atat_role_name="developer")
    assert user.id == user_id


def test_get_or_create_existing_user(user_id):
    Users.get_or_create(user_id, atat_role_name="developer")
    user = Users.get_or_create(user_id, atat_role_name="developer")
    assert user


def test_get_user(user_id):
    Users.create(user_id, "developer")
    user = Users.get(user_id)
    assert user.id == user_id


def test_get_nonexistent_user(user_id):
    Users.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        Users.get(uuid4())


def test_update_user(user_id):
    Users.create(user_id, "developer")
    updated_user = Users.update(user_id, "ccpo")

    assert updated_user.atat_role.name == "ccpo"


def test_update_nonexistent_user(user_id):
    Users.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        Users.update(uuid4(), "ccpo")


def test_update_existing_user_with_nonexistent_role(user_id):
    Users.create(user_id, "developer")
    with pytest.raises(NotFoundError):
        Users.update(user_id, "nonexistent")
