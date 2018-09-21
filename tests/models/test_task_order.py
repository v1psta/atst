from tests.factories import TaskOrderFactory
from tests.assert_util import dict_contains


def test_as_dictionary():
    data = TaskOrderFactory.dictionary()
    real_task_order = TaskOrderFactory.create(**data)
    assert dict_contains(real_task_order.to_dictionary(), data)


def test_budget():
    task_order = TaskOrderFactory.create(
        clin_0001=500,
        clin_0003=200,
        clin_1001=None,
        clin_1003=None,
        clin_2001=None,
        clin_2003=None,
    )
    assert task_order.budget == 700
