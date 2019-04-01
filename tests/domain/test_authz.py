import pytest

from tests.factories import (
    TaskOrderFactory,
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
)
from atst.domain.authz import Authorization, user_can_access
from atst.domain.authz.decorator import user_can_access_decorator
from atst.domain.permission_sets import PermissionSets
from atst.domain.exceptions import UnauthorizedError
from atst.models.permissions import Permissions
from atst.domain.portfolio_roles import PortfolioRoles

from tests.utils import FakeLogger


@pytest.fixture
def invalid_user():
    return UserFactory.create()


@pytest.fixture
def task_order():
    return TaskOrderFactory.create()


def test_is_ko(task_order, invalid_user):
    assert not Authorization.is_ko(invalid_user, task_order)
    assert Authorization.is_ko(task_order.contracting_officer, task_order)


def test_is_cor(task_order, invalid_user):
    assert not Authorization.is_cor(invalid_user, task_order)
    assert Authorization.is_cor(
        task_order.contracting_officer_representative, task_order
    )


def test_is_so(task_order, invalid_user):
    assert Authorization.is_so(task_order.security_officer, task_order)
    assert not Authorization.is_so(invalid_user, task_order)


def test_check_is_ko_or_cor(task_order, invalid_user):
    assert Authorization.check_is_ko_or_cor(
        task_order.contracting_officer_representative, task_order
    )
    assert Authorization.check_is_ko_or_cor(task_order.contracting_officer, task_order)

    with pytest.raises(UnauthorizedError):
        Authorization.check_is_ko_or_cor(invalid_user, task_order)


def test_has_portfolio_permission():
    role_one = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    role_two = PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    port_role = PortfolioRoleFactory.create(permission_sets=[role_one, role_two])
    different_user = UserFactory.create()
    assert Authorization.has_portfolio_permission(
        port_role.user, port_role.portfolio, Permissions.VIEW_PORTFOLIO_REPORTS
    )
    assert not Authorization.has_portfolio_permission(
        port_role.user, port_role.portfolio, Permissions.CREATE_TASK_ORDER
    )
    assert not Authorization.has_portfolio_permission(
        different_user, port_role.portfolio, Permissions.VIEW_PORTFOLIO_REPORTS
    )


def test_user_can_access():
    ccpo = UserFactory.create_ccpo()
    edit_admin = UserFactory.create()
    view_admin = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=edit_admin)
    # factory gives view perms by default
    PortfolioRoleFactory.create(user=view_admin, portfolio=portfolio)

    # check a site-wide permission
    assert user_can_access(ccpo, Permissions.VIEW_AUDIT_LOG)

    with pytest.raises(UnauthorizedError):
        user_can_access(edit_admin, Permissions.VIEW_AUDIT_LOG)

    with pytest.raises(UnauthorizedError):
        user_can_access(view_admin, Permissions.VIEW_AUDIT_LOG)

    # check a portfolio view permission
    assert user_can_access(ccpo, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)
    assert user_can_access(edit_admin, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)
    assert user_can_access(view_admin, Permissions.VIEW_PORTFOLIO, portfolio=portfolio)

    # check a portfolio edit permission
    assert user_can_access(ccpo, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio)
    assert user_can_access(
        edit_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
    )
    with pytest.raises(UnauthorizedError):
        user_can_access(
            view_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
        )

    # check when portfolio_role is disabled
    view_admin_pr = PortfolioRoles.get(portfolio_id=portfolio.id, user_id=view_admin.id)
    PortfolioRoles.disable(portfolio_role=view_admin_pr)
    with pytest.raises(UnauthorizedError):
        user_can_access(
            view_admin, Permissions.EDIT_PORTFOLIO_NAME, portfolio=portfolio
        )


@pytest.fixture
def set_current_user(request_ctx):
    def _set_current_user(user):
        request_ctx.g.current_user = user

    yield _set_current_user

    request_ctx.g.current_user = None


def test_user_can_access_decorator(set_current_user):
    ccpo = UserFactory.create_ccpo()
    edit_admin = UserFactory.create()
    view_admin = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=edit_admin)
    # factory gives view perms by default
    PortfolioRoleFactory.create(user=view_admin, portfolio=portfolio)

    @user_can_access_decorator(Permissions.EDIT_PORTFOLIO_NAME)
    def _edit_portfolio_name(*args, **kwargs):
        return True

    set_current_user(ccpo)
    assert _edit_portfolio_name(portfolio_id=portfolio.id)

    set_current_user(edit_admin)
    assert _edit_portfolio_name(portfolio_id=portfolio.id)

    set_current_user(view_admin)
    with pytest.raises(UnauthorizedError):
        _edit_portfolio_name(portfolio_id=portfolio.id)


def test_user_can_access_decorator_override(set_current_user):
    rando_calrissian = UserFactory.create()
    darth_vader = UserFactory.create()

    def _can_fly_the_millenium_falcon(u, *args, **kwargs):
        if u == rando_calrissian:
            return True
        else:
            raise UnauthorizedError(u, "is not rando")

    @user_can_access_decorator(
        Permissions.EDIT_PORTFOLIO_NAME, override=_can_fly_the_millenium_falcon
    )
    def _cloud_city(*args, **kwargs):
        return True

    set_current_user(rando_calrissian)
    assert _cloud_city()

    set_current_user(darth_vader)
    with pytest.raises(UnauthorizedError):
        assert _cloud_city()


@pytest.fixture
def mock_logger(app):
    real_logger = app.logger
    app.logger = FakeLogger()

    yield app.logger

    app.logger = real_logger


def test_user_can_access_decorator_logs_access(
    set_current_user, monkeypatch, mock_logger
):
    user = UserFactory.create()

    @user_can_access_decorator(Permissions.EDIT_PORTFOLIO_NAME)
    def _do_something(*args, **kwargs):
        return True

    set_current_user(user)

    monkeypatch.setattr(
        "atst.domain.authz.decorator.check_access", lambda *a, **k: True
    )
    _do_something()
    assert len(mock_logger.messages) == 1
    assert "accessed" in mock_logger.messages[0]
    assert "GET" in mock_logger.messages[0]

    def _unauthorized(*a, **k):
        raise UnauthorizedError(user, "do something")

    monkeypatch.setattr("atst.domain.authz.decorator.check_access", _unauthorized)
    with pytest.raises(UnauthorizedError):
        _do_something()

    assert len(mock_logger.messages) == 2
    assert "denied access" in mock_logger.messages[1]
    assert "GET" in mock_logger.messages[1]
