import pytest
from atst.queue import queue, send_mail

# ensure queue is always empty for unit testing
@pytest.fixture(scope="function", autouse=True)
def reset_queue():
    queue.get_queue().empty()
    yield
    queue.get_queue().empty()


def test_send_mail():
    assert len(queue.get_queue()) == 0
    send_mail.queue(
        ["lordvader@geocities.net"], "death start", "how is it coming along?"
    )
    assert len(queue.get_queue()) == 1
