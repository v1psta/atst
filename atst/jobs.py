from flask import current_app as app

from atst.queue import celery
from atst.database import db
from atst.models import EnvironmentJobFailure, EnvironmentRoleJobFailure


class RecordEnvironmentFailure(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if "environment_id" in kwargs:
            failure = EnvironmentJobFailure(
                environment_id=kwargs["environment_id"], task_id=task_id
            )
            db.session.add(failure)
            db.session.commit()


class RecordEnvironmentRoleFailure(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if "environment_role_id" in kwargs:
            failure = EnvironmentRoleJobFailure(
                environment_role_id=kwargs["environment_role_id"], task_id=task_id
            )
            db.session.add(failure)
            db.session.commit()


@celery.task(ignore_result=True)
def send_mail(recipients, subject, body):
    app.mailer.send(recipients, subject, body)


@celery.task(ignore_result=True)
def send_notification_mail(recipients, subject, body):
    app.logger.info(
        "Sending a notification to these recipients: {}\n\nSubject: {}\n\n{}".format(
            recipients, subject, body
        )
    )
    app.mailer.send(recipients, subject, body)
