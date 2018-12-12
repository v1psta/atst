import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.legacy_task_orders import LegacyTaskOrders
from atst.eda_client import MockEDAClient

from tests.factories import LegacyTaskOrderFactory


def test_can_get_task_order():
    new_to = LegacyTaskOrderFactory.create(number="0101969F")
    to = LegacyTaskOrders.get(new_to.number)

    assert to.id == to.id


def test_nonexistent_task_order_raises_without_client():
    with pytest.raises(NotFoundError):
        LegacyTaskOrders.get("some fake number")


def test_nonexistent_task_order_raises_with_client(monkeypatch):
    monkeypatch.setattr(
        "atst.domain.legacy_task_orders.LegacyTaskOrders._client",
        lambda: MockEDAClient(),
    )
    with pytest.raises(NotFoundError):
        LegacyTaskOrders.get("some other fake numer")
