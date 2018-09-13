from atst.domain.audit_log import AuditLog
from atst.domain.requests import Requests
from tests.factories import UserFactory, RequestFactory


def test_log_event():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    event = AuditLog.log_event(user, request, "create request")

    assert event.user == user


def test_get_all_events():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    event = AuditLog.log_event(user, request, "create request")

    assert AuditLog.get_all_events() == [event]


def test_create_request_logs_event():
    user = UserFactory.create()
    Requests.create(user, {})

    assert len(AuditLog.get_all_events()) == 1
