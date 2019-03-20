import pytest

from atst.domain.audit_log import AuditLog
from atst.domain.exceptions import UnauthorizedError
from atst.domain.permission_sets import PermissionSets
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from tests.factories import (
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    ApplicationFactory,
)


@pytest.fixture(scope="function")
def ccpo():
    return UserFactory.create_ccpo()


@pytest.fixture(scope="function")
def developer():
    return UserFactory.create()


@pytest.mark.skip(reason="redo as a route access test")
def test_non_admin_cannot_view_audit_log(developer):
    with pytest.raises(UnauthorizedError):
        AuditLog.get_all_events(developer)


def test_ccpo_can_view_audit_log(ccpo):
    events = AuditLog.get_all_events(ccpo)
    assert len(events) > 0


def test_paginate_audit_log(ccpo):
    user = UserFactory.create()
    for _ in range(100):
        AuditLog.log_system_event(user, action="create")

    events = AuditLog.get_all_events(ccpo, pagination_opts={"per_page": 25, "page": 2})
    assert len(events) == 25


def test_ccpo_can_view_ws_audit_log(ccpo):
    portfolio = PortfolioFactory.create()
    events = AuditLog.get_portfolio_events(ccpo, portfolio)
    assert len(events) > 0


def test_ws_admin_can_view_ws_audit_log():
    portfolio = PortfolioFactory.create()
    admin = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio, user=admin, status=PortfolioRoleStatus.ACTIVE
    )
    events = AuditLog.get_portfolio_events(admin, portfolio)
    assert len(events) > 0


def test_ws_owner_can_view_ws_audit_log():
    portfolio = PortfolioFactory.create()
    events = AuditLog.get_portfolio_events(portfolio.owner, portfolio)
    assert len(events) > 0


@pytest.mark.skip(reason="redo as a route access test")
def test_other_users_cannot_view_portfolio_audit_log():
    with pytest.raises(UnauthorizedError):
        portfolio = PortfolioFactory.create()
        dev = UserFactory.create()
        AuditLog.get_portfolio_events(dev, portfolio)


def test_paginate_ws_audit_log():
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    for _ in range(100):
        AuditLog.log_system_event(
            resource=application, action="create", portfolio=portfolio
        )

    events = AuditLog.get_portfolio_events(
        portfolio.owner, portfolio, pagination_opts={"per_page": 25, "page": 2}
    )
    assert len(events) == 25


def test_ws_audit_log_only_includes_current_ws_events():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    other_portfolio = PortfolioFactory.create(owner=owner)
    # Add some audit events
    application_1 = ApplicationFactory.create(portfolio=portfolio)
    application_2 = ApplicationFactory.create(portfolio=other_portfolio)

    events = AuditLog.get_portfolio_events(portfolio.owner, portfolio)
    for event in events:
        assert event.portfolio_id == portfolio.id or event.resource_id == portfolio.id
        assert (
            not event.portfolio_id == other_portfolio.id
            or event.resource_id == other_portfolio.id
        )
