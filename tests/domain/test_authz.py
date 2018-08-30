from atst.domain.authz import Authorization
from atst.domain.roles import Roles

from tests.factories import RequestFactory, UserFactory


def test_creator_can_view_own_request():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    assert Authorization.can_view_request(user, request)

    other_user = UserFactory.create()
    assert not Authorization.can_view_request(other_user, request)


def test_ccpo_user_can_view_request():
    role = Roles.get("ccpo")
    ccpo_user = UserFactory.create(atat_role=role)
    request = RequestFactory.create()
    assert Authorization.can_view_request(ccpo_user, request)
