from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from .exceptions import NotFoundError


class TaskOrders(object):

    @classmethod
    def get(cls, order_number, client=None):
        try:
            task_order = (
                db.session.query(TaskOrder).filter_by(number=order_number).one()
            )
        except NoResultFound:
            if client:
                task_order = TaskOrders._get_from_eda(order_number, client)
            else:
                raise NotFoundError("task_order")

        return task_order

    @classmethod
    def _get_from_eda(cls, order_number, client):
        to_data = client.get_contract(order_number, status="y")
        if to_data:
            return TaskOrders.create(to_data["contract_no"])
        else:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, order_number):
        task_order = TaskOrder(number=order_number)

        db.session.add(task_order)
        db.session.commit()

        return task_order
