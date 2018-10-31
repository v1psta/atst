from atst.database import db
from atst.models.environment_role import EnvironmentRole
from atst.models.project import Project
from atst.models.environment import Environment


class WorkspaceUser(object):
    def __init__(self, user, workspace_role):
        self.user = user
        self.workspace_role = workspace_role

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
    def role_displayname(self):
        return self.workspace_role.role.display_name

    @property
    def status(self):
        return self.workspace_role.display_status

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
    def environment_roles(self):
        return (
            db.session.query(EnvironmentRole)
            .join(EnvironmentRole.environment)
            .join(Environment.project)
            .join(Project.workspace)
            .filter(Project.workspace_id == self.workspace_id)
            .filter(EnvironmentRole.user_id == self.user_id)
            .all()
        )

    @property
    def has_environment_roles(self):
        return self.num_environment_roles > 0

    def __repr__(self):
        return "<WorkspaceUser(user='{}', role='{}', workspace='{}', num_environment_roles='{}')>".format(
            self.user_name, self.role, self.workspace.name, self.num_environment_roles
        )
