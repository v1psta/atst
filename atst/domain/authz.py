from atst.domain.workspace_users import WorkspaceUsers


class Authorization(object):
    @classmethod
    def has_workspace_permission(cls, user, workspace, permission):
        workspace_user = WorkspaceUsers.get(workspace.id, user.id)
        return permission in workspace_user.permissions()

    @classmethod
    def is_in_workspace(cls, user, workspace):
        return user in workspace.users
