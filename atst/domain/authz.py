from sqlalchemy import exists, and_
from atst.database import db
from atst.models.workspace_role import WorkspaceRole
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.exceptions import NotFoundError


class Authorization(object):
    @classmethod
    def has_workspace_permission(cls, user, workspace, permission):
        try:
            workspace_user = WorkspaceUsers.get(workspace.id, user.id)
        except NotFoundError:
            return False

        return permission in workspace_user.permissions

    @classmethod
    def user_in_workspace(cls, user, workspace):
        return db.session.query(
            exists().where(
                and_(
                    WorkspaceRole.workspace_id == workspace.id,
                    WorkspaceRole.user_id == user.id,
                )
            )
        ).scalar()
