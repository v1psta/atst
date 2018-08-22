from atst.database import db
from atst.models.environment import Environment


class Environments(object):
    @classmethod
    def create(cls, project, name):
        environment = Environment(project=project, name=name)
        db.session.add(environment)
        db.session.commit()
        return environment

    @classmethod
    def create_many(cls, project, names):
        for name in names:
            environment = Environment(project=project, name=name)
            db.session.add(environment)
        db.session.commit()
