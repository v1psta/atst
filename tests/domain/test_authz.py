import pytest

from tests.factories import TaskOrderFactory, UserFactory, PortfolioRoleFactory
from atst.domain.authz import Authorization
from atst.domain.permission_sets import PermissionSets
from atst.domain.exceptions import UnauthorizedError
from atst.models.permissions import Permissions


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
    role_one = PermissionSets.get("view_portfolio_funding")
    role_two = PermissionSets.get("view_portfolio_reports")
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
