from atst.domain.audit_log import AuditLog
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
