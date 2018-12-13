from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from .exceptions import NotFoundError


class TaskOrders(object):
    @classmethod
    def get(cls, task_order_id):
        try:
            task_order = db.session.query(TaskOrder).filter_by(id=task_order_id).one()

            return task_order
        except NoResultFound:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, workspace, creator):
        task_order = TaskOrder(workspace=workspace, creator=creator)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def update(cls, task_order, **kwargs):
        for key, value in kwargs.items():
            setattr(task_order, key, value)

        db.session.add(task_order)
        db.session.commit()

        return task_order
