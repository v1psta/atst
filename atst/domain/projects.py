from atst.database import db
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
