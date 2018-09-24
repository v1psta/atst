from atst.database import db
from atst.models.environment_role import EnvironmentRole
from atst.models.project import Project
from atst.models.environment import Environment


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

    @property
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
        return "active"

    @property
    def num_environment_roles(self):
        return (
            db.session.query(EnvironmentRole)
            .join(EnvironmentRole.environment)
            .join(Environment.project)
            .join(Project.workspace)
            .filter(Project.workspace_id == self.workspace_id)
            .filter(EnvironmentRole.user_id == self.user_id)
            .count()
        )

    @property
    def has_environment_roles(self):
        return self.num_environment_roles > 0
