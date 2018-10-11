from flask_rq2 import RQ
from flask import current_app as app

queue = RQ()


@queue.job
def send_mail(to, subject, body):
    app.mailer.send(to, subject, body)
