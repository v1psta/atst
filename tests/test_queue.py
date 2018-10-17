import pytest
from atst.queue import queue

# ensure queue is always empty for unit testing
@pytest.fixture(scope="function", autouse=True)
def reset_queue():
    queue.get_queue().empty()
    yield
    queue.get_queue().empty()


def test_send_mail():
    initial = len(queue.get_queue())
    queue.send_mail(
        ["lordvader@geocities.net"], "death start", "how is it coming along?"
    )
    assert len(queue.get_queue()) == initial + 1
