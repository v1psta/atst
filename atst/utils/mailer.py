import smtplib
from email.message import EmailMessage


class _HostConnection:
    def __init__(self, server, port, username, password, use_tls=False):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.host = None

    def __enter__(self):
        if self.use_tls:
            self.host = smtplib.SMTP(self.server, self.port)
            self.host.starttls()
        else:
            self.host = smtplib.SMTP_SSL(self.server, self.port)
        self.host.login(self.username, self.password)

        return self.host

    def __exit__(self, *args):
        if self.host:
            self.host.quit()


class BaseMailer:
    def __init__(self, server, port, sender, password, use_tls=False):
        self.server = server
        self.port = port
        self.sender = sender
        self.password = password
        self.use_tls = use_tls
        self.messages = []

    def _message(self, recipients, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        return msg

    def send(self, recipients, subject, body):
        pass


class Mailer(BaseMailer):
    def connection(self):
        return _HostConnection(self.server, self.port, self.sender, self.password, use_tls=self.use_tls)

    def send(self, recipients, subject, body):
        message = self._message(recipients, subject, body)
        with self.connection() as conn:
            conn.send_message(message)


class RedisMailer(BaseMailer):
    def __init__(self, redis, **kwargs):
        super().__init__(**kwargs)
        self.redis = redis
        self._reset()

    def _reset(self):
        self.redis.delete("atat_inbox")

    @property
    def messages(self):
        return [msg.decode() for msg in self.redis.lrange("atat_inbox", 0, -1)]

    def send(self, recipients, subject, body):
        message = self._message(recipients, subject, body)
        self.redis.lpush("atat_inbox", str(message))
