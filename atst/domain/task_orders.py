from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from .exceptions import NotFoundError


class TaskOrders(object):

    @classmethod
    def get(self, order_number):
        try:
            task_order = (
                db.session.query(TaskOrder).filter_by(number=order_number).one()
            )
        except NoResultFound:
            raise NotFoundError("task_order")

        return task_order
