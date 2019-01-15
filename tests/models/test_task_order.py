from atst.models.task_order import TaskOrder, Status

from tests.factories import random_future_date, random_past_date


class TestTaskOrderStatus:
    def test_pending_status(self):
        to = TaskOrder()
        assert to.status == Status.PENDING

        to = TaskOrder(number="42", start_date=random_future_date())
        assert to.status == Status.PENDING

    def test_active_status(self):
        to = TaskOrder(
            number="42", start_date=random_past_date(), end_date=random_future_date()
        )
        assert to.status == Status.ACTIVE

    def test_expired_status(self):
        to = TaskOrder(
            number="42", start_date=random_past_date(), end_date=random_past_date()
        )
        assert to.status == Status.EXPIRED


def test_is_submitted():
    to = TaskOrder()
    assert not to.is_submitted

    to = TaskOrder(number="42")
    assert to.is_submitted
