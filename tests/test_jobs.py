import pytest

from atst.jobs import RecordEnvironmentFailure, RecordEnvironmentRoleFailure

from tests.factories import EnvironmentFactory, EnvironmentRoleFactory


def test_environment_job_failure(celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordEnvironmentFailure)
    def _fail_hard(self, environment_id=None):
        raise ValueError("something bad happened")

    environment = EnvironmentFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_id": environment.id})
    with pytest.raises(ValueError):
        task.get()

    assert environment.job_failures
    job_failure = environment.job_failures[0]
    assert job_failure.task == task


def test_environment_role_job_failure(celery_app, celery_worker):
    @celery_app.task(bind=True, base=RecordEnvironmentRoleFailure)
    def _fail_hard(self, environment_role_id=None):
        raise ValueError("something bad happened")

    role = EnvironmentRoleFactory.create()
    celery_worker.reload()

    # Use apply instead of delay since we are testing the on_failure hook only
    task = _fail_hard.apply(kwargs={"environment_role_id": role.id})
    with pytest.raises(ValueError):
        task.get()

    assert role.job_failures
    job_failure = role.job_failures[0]
    assert job_failure.task == task
