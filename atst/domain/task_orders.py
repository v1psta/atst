from flask import current_app as app

from atst.database import db
from atst.models.clin import CLIN
from atst.models.task_order import TaskOrder
from . import BaseDomainClass


class TaskOrderError(Exception):
    pass


class TaskOrders(BaseDomainClass):
    model = TaskOrder
    resource_name = "task_order"

    SECTIONS = {"app_info": ["portfolio_name"], "funding": [], "oversight": []}

    UNCLASSIFIED_FUNDING = []

    @classmethod
    def create(cls, creator, portfolio_id, number, clins):
        task_order = TaskOrder(
            portfolio_id=portfolio_id, creator=creator, number=number
        )
        db.session.add(task_order)
        db.session.commit()

        TaskOrders.create_clins(task_order.id, clins)

        return task_order

    @classmethod
    def update(cls, task_order_id, number, clins):
        task_order = TaskOrders.get(task_order_id)

        for clin in task_order.clins:
            db.session.delete(clin)
            db.session.commit()

        if number != task_order.number:
            task_order.number = number
            db.session.add(task_order)
            db.session.commit()

        TaskOrders.create_clins(task_order_id, clins)

        return task_order

    @classmethod
    def create_clins(cls, task_order_id, clin_list):
        for clin_data in clin_list:
            clin = CLIN(
                task_order_id=task_order_id,
                number=clin_data["number"],
                loas=clin_data["loas"],
                start_date=clin_data["start_date"],
                end_date=clin_data["end_date"],
                obligated_amount=clin_data["obligated_amount"],
                jedi_clin_type=clin_data["jedi_clin_type"],
            )
            db.session.add(clin)
            db.session.commit()

    @classmethod
    def section_completion_status(cls, task_order, section):
        if section in TaskOrders.mission_owner_sections():
            passed = []
            failed = []

            for attr in TaskOrders.SECTIONS[section]:
                if getattr(task_order, attr) is not None:
                    passed.append(attr)
                else:
                    failed.append(attr)

            if not failed:
                return "complete"
            elif passed and failed:
                return "draft"

        return "incomplete"

    @classmethod
    def all_sections_complete(cls, task_order):
        for section in TaskOrders.SECTIONS.keys():
            if (
                TaskOrders.section_completion_status(task_order, section)
                is not "complete"
            ):
                return False

        return True

    @classmethod
    def mission_owner_sections(cls):
        section_list = TaskOrders.SECTIONS
        if not app.config.get("CLASSIFIED"):
            section_list["funding"] = TaskOrders.UNCLASSIFIED_FUNDING
        return section_list
