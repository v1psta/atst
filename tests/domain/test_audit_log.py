import pytest

from atst.domain.audit_log import AuditLog
from atst.domain.requests import Requests
from atst.domain.exceptions import UnauthorizedError
from tests.factories import UserFactory, RequestFactory


@pytest.fixture(scope="function")
def ccpo():
    return UserFactory.from_atat_role("ccpo")


@pytest.fixture(scope="function")
def developer():
    return UserFactory.from_atat_role("default")


def test_log_event(developer):
    request = RequestFactory.create(creator=developer)
    event = AuditLog.log_event(developer, request, "create request")

    assert event.user == developer


def test_get_all_events(developer, ccpo):
    request = RequestFactory.create(creator=developer)
    event = AuditLog.log_event(developer, request, "create request")

    assert AuditLog.get_all_events(ccpo) == [event]


def test_create_request_logs_event(developer, ccpo):
    Requests.create(developer, {})

    assert len(AuditLog.get_all_events(ccpo)) == 1


def test_non_admin_cannot_view_audit_log(developer):
    with pytest.raises(UnauthorizedError):
        AuditLog.get_all_events(developer)
