from atst.domain.workspace_users import WorkspaceUsers
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


class Authorization(object):
    @classmethod
    def has_workspace_permission(cls, user, workspace, permission):
        return permission in WorkspaceUsers.workspace_user_permissions(workspace, user)

    @classmethod
    def has_atat_permission(cls, user, permission):
        return permission in user.atat_role.permissions

    @classmethod
    def is_in_workspace(cls, user, workspace):
        return user in workspace.users

    @classmethod
    def check_workspace_permission(cls, user, workspace, permission, message):
        if not Authorization.has_workspace_permission(user, workspace, permission):
            raise UnauthorizedError(user, message)

    @classmethod
    def check_atat_permission(cls, user, permission, message):
        if not Authorization.has_atat_permission(user, permission):
            raise UnauthorizedError(user, message)

    @classmethod
    def can_view_audit_log(cls, user):
        return Authorization.has_atat_permission(user, Permissions.VIEW_AUDIT_LOG)

    @classmethod
    def is_ccpo(cls, user):
        return user.atat_role.name == "ccpo"
