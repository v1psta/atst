from flask import current_app as app
import pendulum

from atst.database import db
from atst.queue import celery
from atst.models import EnvironmentJobFailure, EnvironmentRoleJobFailure
from atst.domain.csp.cloud import CloudProviderInterface, GeneralCSPException
from atst.domain.environments import Environments
from atst.models.utils import claim_for_update


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


def do_create_environment(csp: CloudProviderInterface, environment_id=None):
    environment = Environments.get(environment_id)

    with claim_for_update(environment) as environment:

        if environment.cloud_id is not None:
            # TODO: Return value for this?
            return

        user = environment.creator

        # we'll need to do some checking in this job for cases where it's retrying
        # when a failure occured after some successful steps
        # (e.g. if environment.cloud_id is not None, then we can skip first step)

        # credentials either from a given user or pulled from config?
        # if using global creds, do we need to log what user authorized action?
        atat_root_creds = csp.root_creds()

        # user is needed because baseline root account in the environment will
        # be assigned to the requesting user, open question how to handle duplicate
        # email addresses across new environments
        csp_environment_id = csp.create_environment(atat_root_creds, user, environment)
        environment.cloud_id = csp_environment_id
        db.session.add(environment)
        db.session.commit()


def do_create_atat_admin_user(csp: CloudProviderInterface, environment_id=None):
    environment = Environments.get(environment_id)

    with claim_for_update(environment) as environment:
        atat_root_creds = csp.root_creds()

        atat_remote_root_user = csp.create_atat_admin_user(
            atat_root_creds, environment.cloud_id
        )
        environment.root_user_info = atat_remote_root_user
        db.session.add(environment)
        db.session.commit()


def do_create_environment_baseline(csp: CloudProviderInterface, environment_id=None):
    environment = Environments.get(environment_id)

    with claim_for_update(environment) as environment:
        # ASAP switch to use remote root user for provisioning
        atat_remote_root_creds = environment.root_user_info["credentials"]

        baseline_info = csp.create_environment_baseline(
            atat_remote_root_creds, environment.cloud_id
        )
        environment.baseline_info = baseline_info
        db.session.add(environment)
        db.session.commit()


def do_work(fn, task, csp, **kwargs):
    try:
        fn(csp, **kwargs)
    except GeneralCSPException as e:
        raise task.retry(exc=e)


@celery.task(bind=True)
def create_environment(self, environment_id=None, atat_user_id=None):
    do_work(do_create_environment, self, app.csp.cloud, environment_id=environment_id)


@celery.task(bind=True)
def create_atat_admin_user(self, environment_id=None):
    do_work(
        do_create_atat_admin_user, self, app.csp.cloud, environment_id=environment_id
    )


@celery.task(bind=True)
def create_environment_baseline(self, environment_id=None):
    do_work(
        do_create_environment_baseline,
        self,
        app.csp.cloud,
        environment_id=environment_id,
    )


@celery.task(bind=True)
def dispatch_create_environment(self):
    for environment in Environments.get_environments_pending_creation(pendulum.now()):
        create_environment.delay(
            environment_id=environment.id, atat_user_id=environment.creator_id
        )


@celery.task(bind=True)
def dispatch_create_atat_admin_user(self):
    for environment in Environments.get_environments_pending_atat_user_creation(
        pendulum.now()
    ):
        create_atat_admin_user.delay(environment_id=environment.id)


@celery.task(bind=True)
def dispatch_create_environment_baseline(self):
    for environment in Environments.get_environments_pending_baseline_creation(
        pendulum.now()
    ):
        create_environment_baseline.delay(environment_id=environment.id)
