import pytest

import atst
from atst.app import make_app, make_config
from atst.domain.auth import UNPROTECTED_ROUTES as _NO_LOGIN_REQUIRED
import atst.domain.authz as authz

from tests.factories import UserFactory

_NO_ACCESS_CHECK_REQUIRED = _NO_LOGIN_REQUIRED + [
    "task_orders.get_started",  # all users can start a new TO
    "atst.csp_environment_access",  # internal redirect
    "atst.jedi_csp_calculator",  # internal redirect
    "atst.styleguide",  # dev reference
    "dev.test_email",  # dev tool
    "dev.messages",  # dev tool
    "atst.home",  # available to all users
    "users.user",  # available to all users
    "users.update_user",  # available to all users
    "portfolios.accept_invitation",  # available to all users; access control is built into invitation logic
    "atst.catch_all",  # available to all users
    "portfolios.portfolios",  # the portfolios list is scoped to the user separately
]


def protected_routes(app):
    _protected_routes = []

    for rule in app.url_map.iter_rules():
        args = [1] * len(rule.arguments)
        mock_args = dict(zip(rule.arguments, args))
        _n, route = rule.build(mock_args)
        if rule.endpoint in _NO_ACCESS_CHECK_REQUIRED or "/static" in route:
            continue

        _protected_routes.append((rule, route))

    return _protected_routes


sample_config = make_config()
sample_app = make_app(sample_config)
_PROTECTED_ROUTES = protected_routes(sample_app)


class Null:
    """
    Very simple null object. Will return itself for all attribute
    calls:
    > foo = Null()
    > foo.bar.baz == foo
    """

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self


@pytest.mark.parametrize("rule,route", _PROTECTED_ROUTES)
def test_all_protected_routes_have_access_control(
    rule, route, mocker, client, user_session, monkeypatch
):
    """
    This tests that all routes, except the ones in
    _NO_ACCESS_CHECK_REQUIRED, are protected by the access
    decorator.
    """
    # monkeypatch any object lookups that might happen in the access decorator
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.for_user", lambda *a: [])
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.get", lambda *a: None)
    monkeypatch.setattr("atst.domain.task_orders.TaskOrders.get", lambda *a: Null())

    # patch the two internal functions the access decorator uses so
    # that we can check that one or the other was called
    mocker.patch("atst.domain.authz.decorator.user_can_access")
    mocker.patch("atst.domain.authz.decorator.evaluate_exceptions")

    user = UserFactory.create()
    user_session(user)

    method = "get" if "GET" in rule.methods else "post"
    getattr(client, method)(route)

    assert (
        atst.domain.authz.decorator.user_can_access.call_count == 1
        or atst.domain.authz.decorator.evaluate_exceptions.call_count == 1
    ), "no access control for {}".format(rule.endpoint)
