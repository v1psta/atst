from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace_role import WorkspaceRole
from atst.models.workspace_user import WorkspaceUser
from atst.models.user import User

from .roles import Roles
from .users import Users
from .exceptions import NotFoundError


class WorkspaceUsers(object):
    @classmethod
    def get(cls, workspace_id, user_id):
        try:
            user = Users.get(user_id)
        except NoResultFound:
            raise NotFoundError("user")

        try:
            workspace_role = (
                db.session.query(WorkspaceRole)
                .join(User)
                .filter(User.id == user_id, WorkspaceRole.workspace_id == workspace_id)
                .one()
            )
        except NoResultFound:
            workspace_role = None

        return WorkspaceUser(user, workspace_role)

    @classmethod
    def add(cls, user, workspace_id, role_name):
        role = Roles.get(role_name)
        try:
            existing_workspace_role = (
                db.session.query(WorkspaceRole)
                .filter(
                    WorkspaceRole.user == user,
                    WorkspaceRole.workspace_id == workspace_id,
                )
                .one()
            )
            new_workspace_role = existing_workspace_role
            new_workspace_role.role = role
        except NoResultFound:
            new_workspace_role = WorkspaceRole(
                user=user, role_id=role.id, workspace_id=workspace_id
            )

        user.workspace_roles.append(new_workspace_role)
        db.session.add(user)
        db.session.commit()

    @classmethod
    def add_many(cls, workspace_id, workspace_user_dicts):
        workspace_users = []

        for user_dict in workspace_user_dicts:
            try:
                user = Users.get(user_dict["id"])
            except NoResultFound:
                default_role = Roles.get("developer")
                user = User(id=user_dict["id"], atat_role=default_role)

            try:
                role = Roles.get(user_dict["workspace_role"])
            except NoResultFound:
                raise NotFoundError("role")

            try:
                existing_workspace_role = (
                    db.session.query(WorkspaceRole)
                    .filter(
                        WorkspaceRole.user == user,
                        WorkspaceRole.workspace_id == workspace_id,
                    )
                    .one()
                )
                new_workspace_role = existing_workspace_role
                new_workspace_role.role = role
            except NoResultFound:
                new_workspace_role = WorkspaceRole(
                    user=user, role_id=role.id, workspace_id=workspace_id
                )

            user.workspace_roles.append(new_workspace_role)
            workspace_user = WorkspaceUser(user, new_workspace_role)
            workspace_users.append(workspace_user)

            db.session.add(user)

        db.session.commit()

        return workspace_users
