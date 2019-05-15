import pytest

from atst.domain.applications import Applications
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


def test_paginate_audit_log():
    user = UserFactory.create()
    for _ in range(100):
        AuditLog.log_system_event(user, action="create")

    events = AuditLog.get_all_events(pagination_opts={"per_page": 25, "page": 2})
    assert len(events) == 25


def test_paginate_ws_audit_log():
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    for _ in range(100):
        AuditLog.log_system_event(
            resource=application, action="create", portfolio=portfolio
        )

    events = AuditLog.get_portfolio_events(
        portfolio, pagination_opts={"per_page": 25, "page": 2}
    )
    assert len(events) == 25


def test_portfolio_audit_log_only_includes_current_portfolio_events():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    other_portfolio = PortfolioFactory.create(owner=owner)
    # Add some audit events
    application_1 = ApplicationFactory.create(portfolio=portfolio)
    application_2 = ApplicationFactory.create(portfolio=other_portfolio)

    events = AuditLog.get_portfolio_events(portfolio)
    for event in events:
        assert event.portfolio_id == portfolio.id
        assert (
            not event.portfolio_id == other_portfolio.id
            or event.resource_id == other_portfolio.id
        )


def test_portfolio_audit_log_includes_app_and_env_events():
    # TODO: add in events for
    # creating/updating/deleting env_role and app_role
    # creating an app_invitation
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    Applications.update(application, {"name": "Star Cruiser"})

    events = AuditLog.get_portfolio_events(portfolio)

    for event in events:
        assert event.portfolio_id == portfolio.id
        if event.resource_type == 'application':
            assert event.application_id == application.id
    pass


def test_application_audit_log_does_not_include_portfolio_events():
    pass
