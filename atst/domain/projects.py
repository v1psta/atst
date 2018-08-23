from atst.database import db
from atst.models.project import Project


class Projects(object):
    @classmethod
    def create(cls, workspace, name, description):
        project = Project(workspace=workspace, name=name, description=description)

        db.session.add(project)
        db.session.commit()

        return project
