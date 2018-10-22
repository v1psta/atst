import pytest

from atst.models.task_order import Source as TaskOrderSource
from atst.domain.exceptions import NotFoundError
from atst.domain.task_orders import TaskOrders
from atst.eda_client import MockEDAClient

from tests.factories import TaskOrderFactory


def test_can_get_task_order():
    new_to = TaskOrderFactory.create(number="0101969F")
    to = TaskOrders.get(new_to.number)

    assert to.id == to.id


def test_nonexistent_task_order_raises_without_client():
    with pytest.raises(NotFoundError):
        TaskOrders.get("some fake number")


def test_nonexistent_task_order_raises_with_client(monkeypatch):
    monkeypatch.setattr(
        "atst.domain.task_orders.TaskOrders._client", lambda: MockEDAClient()
    )
    with pytest.raises(NotFoundError):
        TaskOrders.get("some other fake numer")


def test_create_attachment(extended_financial_verification_data):
    task_order_data = extended_financial_verification_data.copy()
    task_order_data["pdf"] = task_order_data.pop("task_order")
    task_order = TaskOrders.get_or_create_task_order("abc123", task_order_data)
    assert task_order.pdf
