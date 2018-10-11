import pytest
from atst.utils.mailer import Mailer


class MockHost:
    def __init__(self):
        self.messages = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send_message(self, message):
        self.messages.append(message)


@pytest.fixture
def mail_host():
    return MockHost()


def test_can_send_mail(monkeypatch, mail_host):
    monkeypatch.setattr("atst.utils.mailer.Mailer.connection", lambda *args: mail_host)
    mailer = Mailer("localhost", 456, "leia@rebellion.net", "droidsyourelookingfor")
    message_data = {
        "recipients": ["ben@tattoine.org"],
        "subject": "help",
        "body": "you're my only hope",
    }
    mailer.send(**message_data)
    assert len(mail_host.messages) == 1
    message = mail_host.messages[0]
    assert message["To"] == message_data["recipients"][0]
    assert message["Subject"] == message_data["subject"]
    assert message.get_content().strip() == message_data["body"]


def test_can_save_messages():
    mailer = Mailer(
        "localhost", 456, "leia@rebellion.net", "droidsyourelookingfor", debug=True
    )
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
