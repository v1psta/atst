import pytest
from datetime import datetime
from uuid import uuid4

from atst.domain.users import Users
from atst.domain.exceptions import NotFoundError, AlreadyExistsError, UnauthorizedError

from tests.factories import UserFactory

DOD_ID = "my_dod_id"


def test_create_user():
    user = Users.create(DOD_ID)
    assert user.dod_id == DOD_ID


def test_create_user_with_existing_email():
    Users.create(DOD_ID, email="thisusersemail@usersRus.com")
    with pytest.raises(AlreadyExistsError):
        Users.create(DOD_ID, email="thisusersemail@usersRus.com")


def test_create_user_with_nonexistent_permission_set():
    with pytest.raises(NotFoundError):
        Users.create(DOD_ID, permission_sets=["nonexistent"])


def test_get_or_create_nonexistent_user():
    user = Users.get_or_create_by_dod_id(DOD_ID)
    assert user.dod_id == DOD_ID


def test_get_or_create_existing_user():
    fact_user = UserFactory.create()
    user = Users.get_or_create_by_dod_id(fact_user.dod_id)
    assert user == fact_user


def test_get_user():
    new_user = UserFactory.create()
    user = Users.get(new_user.id)
    assert user.id == new_user.id


def test_get_nonexistent_user():
    with pytest.raises(NotFoundError):
        Users.get(uuid4())


def test_get_user_by_dod_id():
    new_user = UserFactory.create()
    user = Users.get_by_dod_id(new_user.dod_id)
    assert user == new_user


def test_update_user():
    new_user = UserFactory.create()
    updated_user = Users.update(new_user, {"first_name": "Jabba"})
    assert updated_user.first_name == "Jabba"


def test_update_user_with_dod_id():
    new_user = UserFactory.create()
    with pytest.raises(UnauthorizedError) as excinfo:
        Users.update(new_user, {"dod_id": "1234567890"})

    assert "dod_id" in str(excinfo.value)


def test_update_user_with_last_login():
    new_user = UserFactory.create()
    Users.update_last_login(new_user)
    last_login = new_user.last_login
    Users.update_last_login(new_user)
    assert new_user.last_login > last_login
