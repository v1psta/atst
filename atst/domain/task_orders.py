from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.database import db
from atst.models.legacy_task_order import LegacyTaskOrder, Source, FundingType
from .exceptions import NotFoundError
from atst.utils import update_obj


class TaskOrders(object):
    TASK_ORDER_DATA = [
        col.name for col in LegacyTaskOrder.__table__.c if col.name != "id"
    ]

    @classmethod
    def get(cls, order_number):
        try:
            legacy_task_order = (
                db.session.query(LegacyTaskOrder).filter_by(number=order_number).one()
            )
        except NoResultFound:
            if TaskOrders._client():
                legacy_task_order = TaskOrders.get_from_eda(order_number)
            else:
                raise NotFoundError("legacy_task_order")

        return legacy_task_order

    @classmethod
    def get_from_eda(cls, order_number):
        to_data = TaskOrders._client().get_contract(order_number, status="y")
        if to_data:
            # TODO: we need to determine exactly what we're getting and storing from the EDA client
            return TaskOrders.create(
                source=Source.EDA, funding_type=FundingType.PROC, **to_data
            )

        else:
            raise NotFoundError("legacy_task_order")

    @classmethod
    def create(cls, source=Source.MANUAL, **kwargs):
        to_data = {k: v for k, v in kwargs.items() if v not in ["", None]}
        legacy_task_order = LegacyTaskOrder(source=source, **to_data)

        db.session.add(legacy_task_order)
        db.session.commit()

        return legacy_task_order

    @classmethod
    def _client(cls):
        return app.eda_client

    @classmethod
    def update(cls, legacy_task_order, dct):
        updated = update_obj(
            legacy_task_order, dct, ignore_vals=lambda v: v in ["", None]
        )
        db.session.add(updated)
        db.session.commit()
        return updated
