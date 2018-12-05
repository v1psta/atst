import pytest

from atst.filters import dollars, renderAuditEvent
from atst.models import AuditEvent


@pytest.mark.parametrize(
    "input,expected",
    [
        ("0", "$0"),
        ("123.00", "$123"),
        ("1234567", "$1,234,567"),
        ("-1234", "$-1,234"),
        ("one", "$0"),
    ],
)
def test_dollar_fomatter(input, expected):
    assert dollars(input) == expected


def test_render_audit_event_with_known_resource_type():
    event = AuditEvent(resource_type='user')
    result = renderAuditEvent(event)
    assert '<article' in result


def test_render_audit_event_with_unknown_resource_type():
    event = AuditEvent(resource_type='boat')
    result = renderAuditEvent(event)
    assert '<article' in result
