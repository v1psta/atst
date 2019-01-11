from atst.models.task_order import TaskOrder, Status


def test_default_status():
    to = TaskOrder()
    assert to.status == Status.PENDING

    with_args = TaskOrder(number="42")
    assert to.status == Status.PENDING
