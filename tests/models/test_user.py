import pytest

from atst.models.user import User

from tests.factories import UserFactory


def test_profile_complete_with_all_info():
    user = UserFactory.create()
    assert user.profile_complete


@pytest.mark.parametrize("missing_field", User.REQUIRED_FIELDS)
def test_profile_complete_with_missing_info(missing_field):
    user = UserFactory.create()
    setattr(user, missing_field, None)
    assert not user.profile_complete
