from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.database import db
from atst.models.task_order import TaskOrder, Source, FundingType
from atst.models.attachment import Attachment
from .exceptions import NotFoundError
from atst.utils import drop, update_obj


class TaskOrders(object):
    TASK_ORDER_DATA = [col.name for col in TaskOrder.__table__.c if col.name != "id"]

    @classmethod
    def get(cls, order_number):
        try:
            task_order = (
                db.session.query(TaskOrder).filter_by(number=order_number).one()
            )
        except NoResultFound:
            if TaskOrders._client():
                task_order = TaskOrders.get_from_eda(order_number)
            else:
                raise NotFoundError("task_order")

        return task_order

    @classmethod
    def get_from_eda(cls, order_number):
        to_data = TaskOrders._client().get_contract(order_number, status="y")
        if to_data:
            # TODO: we need to determine exactly what we're getting and storing from the EDA client
            return TaskOrders.create(
                source=Source.EDA, funding_type=FundingType.PROC, **to_data
            )

        else:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, source=Source.MANUAL, **kwargs):
        to_data = {k: v for k, v in kwargs.items() if v not in ["", None]}
        task_order = TaskOrder(source=source, **to_data)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def _client(cls):
        return app.eda_client

    @classmethod
    def update(cls, task_order, dct):
        updated = update_obj(task_order, dct)
        db.session.add(updated)
        db.session.commit()
        return updated
