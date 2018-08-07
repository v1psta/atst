import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.task_orders import TaskOrders

from tests.factories import TaskOrderFactory


@pytest.fixture(scope="function")
def new_task_order(session):
    def make_task_order(**kwargs):
        to = TaskOrderFactory.create(**kwargs)
        session.add(to)
        session.commit()

        return to

    return make_task_order


def test_can_get_task_order(new_task_order):
    new_to = new_task_order(number="0101969F")
    to = TaskOrders.get(new_to.number)

    assert to.id == to.id


def test_nonexistent_task_order_raises():
    with pytest.raises(NotFoundError):
        TaskOrders.get("some fake number")
