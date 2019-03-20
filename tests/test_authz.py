import pytest

import atst
from atst.app import make_app, make_config
from atst.domain.auth import UNPROTECTED_ROUTES as _NO_LOGIN_REQUIRED
import atst.domain.authz as authz

from tests.factories import UserFactory

_NO_ACCESS_CHECK_REQUIRED = _NO_LOGIN_REQUIRED + [
    "task_orders.get_started",
    "atst.csp_environment_access",
    "atst.jedi_csp_calculator",
    "atst.styleguide",
    "dev.test_email",
    "dev.messages",
    "atst.home",
    "users.user",
    "users.update_user",
    "portfolios.accept_invitation",
    "atst.catch_all",
    "portfolios.portfolios",
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


_PROTECTED_ROUTES = protected_routes(make_app(make_config()))


class Null:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self


@pytest.mark.parametrize("rule,route", _PROTECTED_ROUTES)
def test_all_protected_routes_have_access_control(
    rule, route, mocker, client, user_session, monkeypatch
):
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.for_user", lambda *a: [])
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.get", lambda *a: None)
    monkeypatch.setattr("atst.domain.task_orders.TaskOrders.get", lambda *a: Null())

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
