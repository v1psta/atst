from celery.result import AsyncResult
from sqlalchemy import Column, String, Integer


class JobFailureMixin(object):
    id = Column(Integer(), primary_key=True)
    task_id = Column(String(), nullable=False)

    @property
    def task(self):
        if not hasattr(self, "_task"):
            self._task = AsyncResult(self.task_id)

        return self._task
