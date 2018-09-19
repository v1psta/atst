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
