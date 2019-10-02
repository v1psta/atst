import pendulum
import pytest
import threading
import tempfile

from atst.queue import update_celery

from tests import factories


@pytest.fixture()
def integration_celery_app(app, celery_app):
    celery = update_celery(celery_app, app)
    celery.conf["CELERYBEAT_SCHEDULE"]["beat-dispatch_create_environment"][
        "schedule"
    ] = 1
    return celery


@pytest.fixture(scope="function")
def celery_beat(integration_celery_app):
    with tempfile.NamedTemporaryFile() as tmp:
        beat_kwargs = {
            "app": integration_celery_app,
            "schedule": tmp.name,
            "max_interval": None,
            "scheduler": "celery.beat:PersistentScheduler",
            "loglevel": "info",
        }
        beat = integration_celery_app.Beat(**beat_kwargs)

        t = threading.Thread(target=beat.run, daemon=True)
        t.start()

        yield beat

        t.join(2)


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
