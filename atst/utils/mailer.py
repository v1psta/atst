import smtplib
from email.message import EmailMessage
from collections import deque


class _HostConnection:
    def __init__(self, server, port, username, password, use_tls=False):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.host = None

    def __enter__(self):
        self.host = smtplib.SMTP_SSL(self.server, self.port)
        if self.use_tls:
            self.host.starttls()
        self.host.login(self.username, self.password)

        return self.host

    def __exit__(self, *args):
        if self.host:
            self.host.quit()


class Mailer:
    def __init__(self, server, port, sender, password, use_tls=False, debug=False):
        self.server = server
        self.port = port
        self.sender = sender
        self.password = password
        self.use_tls = use_tls
        self.debug = debug
        self.messages = deque(maxlen=50)

    def connection(self):
        return _HostConnection(self.server, self.port, self.sender, self.password)

    def _message(self, recipients, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        return msg

    def send(self, recipients, subject, body):
        message = self._message(recipients, subject, body)
        if self.debug:
            self.messages.appendleft(message)
        else:
            with self.connection() as conn:
                conn.send_message(message)


def _map_config(config):
    return {
        "server": config.get("MAIL_SERVER"),
        "port": config.get("MAIL_PORT"),
        "sender": config.get("MAIL_SENDER"),
        "password": config.get("MAIL_PASSWORD"),
        "use_tls": config.get("MAIL_TLS", False),
        "debug": config.get("DEBUG", False),
    }


def make_mailer(app):
    config = _map_config(app.config)
    mailer = Mailer(**config)
    app.mailer = mailer
