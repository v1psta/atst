import pytest

from atst.domain.audit_log import AuditLog
from atst.domain.exceptions import UnauthorizedError
from tests.factories import UserFactory


@pytest.fixture(scope="function")
def ccpo():
    return UserFactory.from_atat_role("ccpo")


@pytest.fixture(scope="function")
def developer():
    return UserFactory.from_atat_role("default")


def test_non_admin_cannot_view_audit_log(developer):
    with pytest.raises(UnauthorizedError):
        AuditLog.get_all_events(developer)


def test_ccpo_can_iview_audit_log(ccpo):
    AuditLog.get_all_events(ccpo)


def test_paginate_audit_log(ccpo):
    user = UserFactory.create()
    for _ in range(100):
        AuditLog.log_system_event(user, action="create")

    events = AuditLog.get_all_events(ccpo, pagination={"per_page": 25, "page": 2})
    assert len(events) == 25
