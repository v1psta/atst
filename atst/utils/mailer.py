from contextlib import contextmanager
import smtplib
from email.message import EmailMessage


class MailConnection(object):
    def send(self, message):
        raise NotImplementedError()

    @property
    def messages(self):
        raise NotImplementedError()


class SMTPConnection(MailConnection):
    def __init__(self, server, port, username, password, use_tls=False):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    @contextmanager
    def _host(self):
        host = None

        if self.use_tls:
            host = smtplib.SMTP(self.server, self.port)
            host.starttls()
        else:
            host = smtplib.SMTP_SSL(self.server, self.port)
        host.login(self.username, self.password)

        yield host

        host.quit()

    @property
    def messages(self):
        return []

    def send(self, message):
        with self._host() as host:
            host.send_message(message)


class RedisConnection(MailConnection):
    def __init__(self, redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis
        self._reset()

    def _reset(self):
        self.redis.delete("atat_inbox")

    @property
    def messages(self):
        return [msg.decode() for msg in self.redis.lrange("atat_inbox", 0, -1)]

    def send(self, message):
        self.redis.lpush("atat_inbox", str(message))


class Mailer(object):
    def __init__(self, connection, sender):
        self.connection = connection
        self.sender = sender

    def _message(self, recipients, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        return msg

    def send(self, recipients, subject, body):
        message = self._message(recipients, subject, body)
        self.connection.send(message)

    @property
    def messages(self):
        return self.connection.messages
