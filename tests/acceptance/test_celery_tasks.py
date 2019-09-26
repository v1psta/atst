import pendulum
import pytest
from celery.platforms import detached
import threading

from atst.queue import BEAT_SCHEDULE, celery

from tests import factories


@pytest.fixture(scope="session")
def celery_config():
    return dict(celery.conf)


@pytest.fixture(scope="function")
def celery_beat(celery_app):
    beat_kwargs = {
        "app": celery_app,
        "schedule": "celerybeat-schedule",
        "max_interval": None,
        "scheduler": "celery.beat:PersistentScheduler",
        "loglevel": "fatal",
    }
    # the beat worker still doesn't have the right config; doesn't get beat
    # schedule, etc
    beat = celery_app.Beat(**beat_kwargs)

    t = threading.Thread(target=beat.run)
    t.start()

    yield beat

    from celery.worker import state

    state.should_terminate = 0
    t.join(10)
    state.should_terminate = None


# @pytest.fixture(scope='session')
# def celery_worker_parameters(celery_config):
#     return {
#         "beat": True,
#         **celery_config
#     }


def test_environment_provisioning(app, session, celery_beat, celery_worker):
    portfolio = factories.PortfolioFactory.create(
        applications=[{"name": "new app", "environments": [{"name": "some env"}]}]
    )
    task_order = factories.TaskOrderFactory.create(
        portfolio=portfolio,
        clins=[
            factories.CLINFactory.create(
                start_date=pendulum.now().subtract(days=1),
                end_date=pendulum.now().add(days=1),
            )
        ],
    )
    new_env = portfolio.applications[0].environments[0]
