from celery import Celery

celery = Celery(__name__)


def update_celery(celery, app):
    celery.conf.update(app.config)
    celery.conf.CELERYBEAT_SCHEDULE = {}

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
