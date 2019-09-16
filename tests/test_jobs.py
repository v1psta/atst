import pendulum
import pytest
from uuid import uuid4
from unittest.mock import Mock

from atst.models import Environment
from atst.domain.csp.cloud import MockCloudProvider
from atst.jobs import (
    RecordEnvironmentFailure,
    RecordEnvironmentRoleFailure,
    do_create_environment,
    do_create_atat_admin_user,
    do_create_environment_baseline,
    dispatch_create_environment,
    dispatch_create_atat_admin_user,
    dispatch_create_environment_baseline,
)
from tests.factories import (
    EnvironmentFactory,
    EnvironmentRoleFactory,
    UserFactory,
    PortfolioFactory,
)


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


now = pendulum.now()
yesterday = now.subtract(days=1)
tomorrow = now.add(days=1)
from atst.domain.environments import Environments


@pytest.fixture(autouse=True, scope="function")
def csp():
    return Mock(wraps=MockCloudProvider({}, with_delay=False, with_failure=False))


def test_create_environment_job(session, csp):
    user = UserFactory.create()
    environment = EnvironmentFactory.create()
    do_create_environment(csp, environment.id, user.id)

    environment_id = environment.id
    del environment

    updated_environment = session.query(Environment).get(environment_id)

    assert updated_environment.cloud_id


def test_create_environment_job_is_idempotent(csp, session):
    user = UserFactory.create()
    environment = EnvironmentFactory.create(cloud_id=uuid4().hex)
    do_create_environment(csp, environment.id, user.id)

    csp.create_environment.assert_not_called()


def test_create_atat_admin_user(csp, session):
    environment = EnvironmentFactory.create(cloud_id="something")
    do_create_atat_admin_user(csp, environment.id)

    environment_id = environment.id
    del environment
    updated_environment = session.query(Environment).get(environment_id)

    assert updated_environment.root_user_info


def test_create_environment_baseline(csp, session):
    environment = EnvironmentFactory.create(
        root_user_info={"credentials": csp.root_creds()}
    )
    do_create_environment_baseline(csp, environment.id)

    environment_id = environment.id
    del environment
    updated_environment = session.query(Environment).get(environment_id)

    assert updated_environment.baseline_info


def test_dispatch_create_environment(session, monkeypatch):
    portfolio = PortfolioFactory.create(
        applications=[{"environments": [{}]}],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_environment", mock)
    environment = portfolio.applications[0].environments[0]

    dispatch_create_environment.run()

    mock.delay.assert_called_once_with(
        environment_id=environment.id, atat_user_id=environment.creator_id
    )


def test_dispatch_create_atat_admin_user(session, monkeypatch):
    portfolio = PortfolioFactory.create(
        applications=[
            {"environments": [{"cloud_id": uuid4().hex, "root_user_info": None}]}
        ],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_atat_admin_user", mock)
    environment = portfolio.applications[0].environments[0]

    dispatch_create_atat_admin_user.run()

    mock.delay.assert_called_once_with(environment_id=environment.id)


def test_dispatch_create_environment_baseline(session, monkeypatch):
    portfolio = PortfolioFactory.create(
        applications=[
            {
                "environments": [
                    {
                        "cloud_id": uuid4().hex,
                        "root_user_info": {},
                        "baseline_info": None,
                    }
                ]
            }
        ],
        task_orders=[
            {
                "create_clins": [
                    {
                        "start_date": pendulum.now().subtract(days=1),
                        "end_date": pendulum.now().add(days=1),
                    }
                ]
            }
        ],
    )
    mock = Mock()
    monkeypatch.setattr("atst.jobs.create_environment_baseline", mock)
    environment = portfolio.applications[0].environments[0]

    dispatch_create_environment_baseline.run()

    mock.delay.assert_called_once_with(environment_id=environment.id)
