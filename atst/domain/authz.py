from atst.domain.workspace_roles import WorkspaceRoles
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


class Authorization(object):
    @classmethod
    def has_workspace_permission(cls, user, workspace, permission):
        return permission in WorkspaceRoles.workspace_role_permissions(workspace, user)

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

    @classmethod
    def check_task_order_permission(cls, user, task_order, permission, message):
        if Authorization._check_is_task_order_officer(task_order, user):
            return True

        Authorization.check_workspace_permission(
            user, task_order.workspace, permission, message
        )

    @classmethod
    def _check_is_task_order_officer(cls, task_order, user):
        for officer in [
            "contracting_officer",
            "contracting_officer_representative",
            "security_officer",
        ]:
            if getattr(task_order, officer, None) == user:
                return True

        return False
