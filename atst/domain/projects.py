from atst.database import db
from atst.domain.authz import Authorization
from atst.domain.environments import Environments
from atst.domain.exceptions import NotFoundError
from atst.models.permissions import Permissions
from atst.models.project import Project


class Projects(object):
    @classmethod
    def create(cls, user, workspace, name, description, environment_names):
        project = Project(workspace=workspace, name=name, description=description)
        Environments.create_many(project, environment_names)

        for environment in project.environments:
            Environments.add_member(user, environment, user)

        db.session.add(project)
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
