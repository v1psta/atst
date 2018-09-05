class WorkspaceUser(object):
    def __init__(self, user, workspace_role):
        self.user = user
        self.workspace_role = workspace_role

    def permissions(self):
        atat_permissions = set(self.user.atat_role.permissions)
        workspace_permissions = (
            [] if self.workspace_role is None else self.workspace_role.role.permissions
        )
        return set(workspace_permissions).union(atat_permissions)

    @property
    def workspace(self):
        return self.workspace_role.workspace

    def workspace_id(self):
        return self.workspace_role.workspace_id

    @property
    def user_id(self):
        return self.user.id

    @property
    def user_name(self):
        return self.user.full_name

    @property
    def role(self):
        return self.workspace_role.role.name

    @property
    def status(self):
        return "radical"
