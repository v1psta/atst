from atst.domain.workspace_users import WorkspaceUsers
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


class Authorization(object):
    @classmethod
    def has_workspace_permission(cls, user, workspace, permission):
        workspace_user = WorkspaceUsers.get(workspace.id, user.id)
        return permission in workspace_user.permissions()

    @classmethod
    def is_in_workspace(cls, user, workspace):
        return user in workspace.users

    @classmethod
    def can_view_request(cls, user, request):
        if (
            Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST
            in user.atat_permissions
        ):
            return True
        elif request.creator == user:
            return True

        return False

    @classmethod
    def check_workspace_permission(cls, user, workspace, permission, message):
        if not Authorization.has_workspace_permission(user, workspace, permission):
            raise UnauthorizedError(user, message)
