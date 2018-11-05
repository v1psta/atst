from atst.database import db
from atst.domain.authz import Authorization
from atst.domain.environments import Environments
from atst.domain.exceptions import NotFoundError
from atst.models.permissions import Permissions
from atst.models.project import Project
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole


class Projects(object):
    @classmethod
    def create(cls, user, workspace, name, description, environment_names):
        project = Project(workspace=workspace, name=name, description=description)
        db.session.add(project)

        Environments.create_many(project, environment_names)

        db.session.commit()
        return project

    @classmethod
    def get(cls, user, workspace, project_id):
        # TODO: this should check permission for this particular project
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
            "view project in workspace",
        )

        try:
            project = db.session.query(Project).filter_by(id=project_id).one()
        except NoResultFound:
            raise NotFoundError("project")

        return project

    @classmethod
    def for_user(self, user, workspace):
        return (
            db.session.query(Project)
            .join(Environment)
            .join(EnvironmentRole)
            .filter(Project.workspace_id == workspace.id)
            .filter(EnvironmentRole.user_id == user.id)
            .all()
        )

    @classmethod
    def get_all(cls, user, workspace_role, workspace):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.VIEW_APPLICATION_IN_WORKSPACE,
            "view project in workspace",
        )

        try:
            projects = (
                db.session.query(Project).filter_by(workspace_id=workspace.id).all()
            )
        except NoResultFound:
            raise NotFoundError("projects")

        return projects

    @classmethod
    def update(cls, user, workspace, project, new_data):
        if "name" in new_data:
            project.name = new_data["name"]
        if "description" in new_data:
            project.description = new_data["description"]

        db.session.add(project)
        db.session.commit()

        return project
