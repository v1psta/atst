from flask import current_app as app

from atst.queue import celery


@celery.task()
def send_mail(recipients, subject, body):
    app.mailer.send(recipients, subject, body)


@celery.task()
def send_notification_mail(recipients, subject, body):
    app.logger.info(
        "Sending a notification to these recipients: {}\n\nSubject: {}\n\n{}".format(
            recipients, subject, body
        )
    )
    app.mailer.send(recipients, subject, body)
