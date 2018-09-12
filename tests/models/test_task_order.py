from atst.models.task_order import TaskOrder

from tests.factories import TaskOrderFactory


def test_as_dictionary():
    data = TaskOrderFactory.dictionary()
    real_task_order = TaskOrderFactory.create(**data)
    assert real_task_order.to_dictionary() == data
