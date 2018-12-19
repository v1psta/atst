from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from .exceptions import NotFoundError


class TaskOrders(object):
    SECTIONS = {
        "app_info": [
            "scope",
            "defense_component",
            "app_migration",
            "native_apps",
            "complexity",
            "dev_team",
            "team_experience",
        ],
        "funding": [
            "start_date",
            "end_date",
            "clin_01",
            "clin_02",
            "clin_03",
            "clin_04",
        ],
        "oversight": [
            "ko_first_name",
            "ko_last_name",
            "ko_email",
            "ko_dod_id",
            "cor_first_name",
            "cor_last_name",
            "cor_email",
            "cor_dod_id",
            "so_first_name",
            "so_last_name",
            "so_email",
            "so_dod_id",
        ],
    }

    @classmethod
    def get(cls, task_order_id):
        try:
            task_order = db.session.query(TaskOrder).filter_by(id=task_order_id).one()

            return task_order
        except NoResultFound:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, workspace, creator, commit=False):
        task_order = TaskOrder(workspace=workspace, creator=creator)

        db.session.add(task_order)

        if commit:
            db.session.commit()

        return task_order

    @classmethod
    def update(cls, task_order, **kwargs):
        for key, value in kwargs.items():
            setattr(task_order, key, value)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def is_section_complete(cls, task_order, section):
        if section in TaskOrders.SECTIONS:
            for attr in TaskOrders.SECTIONS[section]:
                if getattr(task_order, attr) is None:
                    return False

            return True

        else:
            return False

    @classmethod
    def all_sections_complete(cls, task_order):
        for section in TaskOrders.SECTIONS.keys():
            if not TaskOrders.is_section_complete(task_order, section):
                return False

        return True
