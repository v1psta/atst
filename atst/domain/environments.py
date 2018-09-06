from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole, CSPRole


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

    @classmethod
    def add_member(cls, user, environment, member):
        environment_user = EnvironmentRole(
            user=member, environment=environment, role=CSPRole.NONSENSE_ROLE.value
        )
        db.session.add(environment_user)
        db.session.commit()

        return environment
