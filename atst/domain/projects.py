from atst.database import db
from atst.domain.exceptions import NotFoundError
from atst.models.project import Project
from atst.domain.environments import Environments


class Projects(object):
    @classmethod
    def create(cls, workspace, name, description, environment_names):
        project = Project(workspace=workspace, name=name, description=description)
        Environments.create_many(project, environment_names)

        db.session.add(project)
        db.session.commit()

        return project

    @classmethod
    def get(cls, user, workspace, project_id):
        # TODO: this should check permission for this particular project
        Authorization.check_workspace_permission(
            user, workspace, Permissions.VIEW_APPLICATION_IN_WORKSPACE,
        )

        try:
            project = db.session.query(Project).filter_by(id=project_id).one()
        except NoResultFound:
            raise NotFoundError("project")

        return project
