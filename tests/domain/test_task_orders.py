import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.task_orders import TaskOrders

from tests.factories import TaskOrderFactory


def test_can_get_task_order():
    new_to = TaskOrderFactory.create(number="0101969F")
    to = TaskOrders.get(new_to.number)

    assert to.id == to.id


def test_nonexistent_task_order_raises():
    with pytest.raises(NotFoundError):
        TaskOrders.get("some fake number")
