from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.database import db
from atst.models.task_order import TaskOrder, Source, FundingType
from atst.models.attachment import Attachment
from .exceptions import NotFoundError


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
                task_order = TaskOrders._get_from_eda(order_number)
            else:
                raise NotFoundError("task_order")

        return task_order

    @classmethod
    def _get_from_eda(cls, order_number):
        to_data = TaskOrders._client().get_contract(order_number, status="y")
        if to_data:
            # TODO: we need to determine exactly what we're getting and storing from the EDA client
            return TaskOrders.create(
                number=to_data["contract_no"],
                source=Source.EDA,
                funding_type=FundingType.PROC,
            )

        else:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, **kwargs):
        task_order = TaskOrder(**kwargs)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def _client(cls):
        return app.eda_client

    @classmethod
    def get_or_create_task_order(cls, number, task_order_data=None):
        try:
            return TaskOrders.get(number)

        except NotFoundError:
            if task_order_data:
                pdf_file = task_order_data.pop("pdf")
                # should catch the error here
                attachment = Attachment.attach(pdf_file)
                return TaskOrders.create(
                    **task_order_data,
                    number=number,
                    source=Source.MANUAL,
                    pdf=attachment,
                )
