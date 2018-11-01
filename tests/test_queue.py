def test_send_mail(queue):
    queue.send_mail(
        ["lordvader@geocities.net"], "death start", "how is it coming along?"
    )
    assert len(queue.get_queue()) == 1
