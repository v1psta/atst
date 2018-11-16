from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace_role import WorkspaceRole, Status as WorkspaceRoleStatus
from atst.models.user import User

from .roles import Roles
from .users import Users
from .exceptions import NotFoundError


MEMBER_STATUSES = [
    {"name": "active", "display_name": "Active"},
    {"name": "revoked", "display_name": "Revoked"},
    {"name": "expired", "display_name": "Invite expired"},
    {"name": "error", "display_name": "Error on invite"},
    {"name": "pending", "display_name": "Pending"},
    {"name": "unknown", "display_name": "Unknown errors"},
]


class WorkspaceRoles(object):
    @classmethod
    def get(cls, workspace_id, user_id):
        try:
            workspace_role = (
                db.session.query(WorkspaceRole)
                .join(User)
                .filter(User.id == user_id, WorkspaceRole.workspace_id == workspace_id)
                .one()
            )
        except NoResultFound:
            workspace_role = None

        return workspace_role

    @classmethod
    def _get_active_workspace_role(cls, workspace_id, user_id):
        try:
            return (
                db.session.query(WorkspaceRole)
                .join(User)
                .filter(User.id == user_id, WorkspaceRole.workspace_id == workspace_id)
                .filter(WorkspaceRole.status == WorkspaceRoleStatus.ACTIVE)
                .one()
            )
        except NoResultFound:
            return None

    @classmethod
    def workspace_role_permissions(cls, workspace, user):
        workspace_role = WorkspaceRoles._get_active_workspace_role(
            workspace.id, user.id
        )
        atat_permissions = set(user.atat_role.permissions)
        workspace_permissions = (
            [] if workspace_role is None else workspace_role.role.permissions
        )
        return set(workspace_permissions).union(atat_permissions)

    @classmethod
    def _get_workspace_role(cls, user, workspace_id):
        try:
            existing_workspace_role = (
                db.session.query(WorkspaceRole)
                .filter(
                    WorkspaceRole.user == user,
                    WorkspaceRole.workspace_id == workspace_id,
                )
                .one()
            )
            return existing_workspace_role
        except NoResultFound:
            raise NotFoundError("workspace role")

    @classmethod
    def add(cls, user, workspace_id, role_name):
        role = Roles.get(role_name)

        new_workspace_role = None
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

        return new_workspace_role

    @classmethod
    def update_role(cls, member, role_name):
        new_role = Roles.get(role_name)
        # necessary?
        workspace_role = WorkspaceRoles._get_workspace_role(
            member.user, member.workspace_id
        )
        # why not just member.role = new_role?
        workspace_role.role = new_role

        db.session.add(workspace_role)
        db.session.commit()
        return workspace_role

    @classmethod
    def add_many(cls, workspace_id, workspace_role_dicts):
        workspace_roles = []

        for user_dict in workspace_role_dicts:
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
            workspace_roles.append(new_workspace_role)

            db.session.add(user)

        db.session.commit()

        return workspace_roles

    @classmethod
    def enable(cls, workspace_role):
        ws_role = WorkspaceRoles._get_workspace_role(
            workspace_role.user, workspace_role.workspace_id
        )
        ws_role.status = WorkspaceRoleStatus.ACTIVE

        db.session.add(ws_role)
        db.session.commit()
