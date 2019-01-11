from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from atst.models.permissions import Permissions
from atst.domain.workspaces import Workspaces
from atst.domain.authz import Authorization
from .exceptions import NotFoundError


class TaskOrderError(Exception):
    pass


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
            "performance_length",
            "start_date",
            # "pdf",
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
            "ko_phone_number",
            "ko_dod_id",
            "cor_first_name",
            "cor_last_name",
            "cor_email",
            "cor_phone_number",
            "cor_dod_id",
            "so_first_name",
            "so_last_name",
            "so_email",
            "so_phone_number",
            "so_dod_id",
        ],
    }

    @classmethod
    def get(cls, user, task_order_id):
        try:
            task_order = db.session.query(TaskOrder).filter_by(id=task_order_id).one()
            Authorization.check_task_order_permission(
                user, task_order, Permissions.VIEW_TASK_ORDER, "view task order"
            )

            return task_order
        except NoResultFound:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, creator, workspace):
        Authorization.check_workspace_permission(
            creator, workspace, Permissions.UPDATE_TASK_ORDER, "add task order"
        )
        task_order = TaskOrder(workspace=workspace, creator=creator)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def update(cls, user, task_order, **kwargs):
        Authorization.check_task_order_permission(
            user, task_order, Permissions.UPDATE_TASK_ORDER, "update task order"
        )

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

    OFFICERS = [
        "contracting_officer",
        "contracting_officer_representative",
        "security_officer",
    ]

    @classmethod
    def add_officer(cls, user, task_order, officer_type, officer_data):
        Authorization.check_workspace_permission(
            user,
            task_order.workspace,
            Permissions.ADD_TASK_ORDER_OFFICER,
            "add task order officer",
        )

        if officer_type in TaskOrders.OFFICERS:
            workspace = task_order.workspace

            existing_member = next(
                (
                    member
                    for member in workspace.members
                    if member.user.dod_id == officer_data["dod_id"]
                ),
                None,
            )

            if existing_member:
                workspace_user = existing_member.user
            else:
                member = Workspaces.create_member(
                    user, workspace, {**officer_data, "workspace_role": "officer"}
                )
                workspace_user = member.user

            setattr(task_order, officer_type, workspace_user)

            db.session.add(task_order)
            db.session.commit()

            return workspace_user
        else:
            raise TaskOrderError(
                "{} is not an officer role on task orders".format(officer_type)
            )
