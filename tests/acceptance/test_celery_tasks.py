import pendulum
import pytest
from celery.platforms import detached
import threading

from atst.queue import celery

from tests import factories


@pytest.fixture(scope="session")
def celery_config():
    conf = dict(celery.conf)
    conf["CELERYBEAT_SCHEDULE"]["beat-dispatch_create_environment"]["schedule"] = 1
    return conf


import tempfile


@pytest.fixture(scope="function")
def celery_beat(celery_app):
    tmp = tempfile.NamedTemporaryFile()
    beat_kwargs = {
        "app": celery_app,
        "schedule": tmp.name,
        "max_interval": None,
        "scheduler": "celery.beat:PersistentScheduler",
        "loglevel": "fatal",
    }
    # the beat worker still doesn't have the right config; doesn't get beat
    # schedule, etc
    beat = celery_app.Beat(**beat_kwargs)

    t = threading.Thread(target=beat.run, daemon=True)
    t.start()

    yield beat

    t.join(10)


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
