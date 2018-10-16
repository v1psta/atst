import pytest
from atst.utils.mailer import Mailer, Mailer, MailConnection, RedisConnection


class MockConnection(MailConnection):
    def __init__(self):
        self._messages = []

    def send(self, message):
        self._messages.append(message)

    @property
    def messages(self):
        return self._messages


@pytest.fixture
def mailer():
    return Mailer(MockConnection(), "test@atat.com")


def test_mailer_can_send_mail(mailer):
    message_data = {
        "recipients": ["ben@tattoine.org"],
        "subject": "help",
        "body": "you're my only hope",
    }
    mailer.send(**message_data)
    assert len(mailer.messages) == 1
    message = mailer.messages[0]
    assert message["To"] == message_data["recipients"][0]
    assert message["Subject"] == message_data["subject"]
    assert message.get_content().strip() == message_data["body"]


def test_redis_mailer_can_save_messages(app):
    mailer = Mailer(RedisConnection(app.redis), "test@atat.com")
    message_data = {
        "recipients": ["ben@tattoine.org"],
        "subject": "help",
        "body": "you're my only hope",
    }
    mailer.send(**message_data)
    assert len(mailer.messages) == 1
    message = mailer.messages[0]
    assert message_data["recipients"][0] in message
    assert message_data["subject"] in message
    assert message_data["body"] in message
