from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole, CSPRole
from atst.models.project import Project

from .exceptions import NotFoundError


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
    def add_member(cls, user, environment, member, role=CSPRole.NONSENSE_ROLE):
        environment_user = EnvironmentRole(
            user=member, environment=environment, role=role.value
        )
        db.session.add(environment_user)
        db.session.commit()

        return environment

    @classmethod
    def for_user(cls, user, project):
        return (
            db.session.query(Environment)
            .join(EnvironmentRole)
            .join(Project)
            .filter(EnvironmentRole.user_id == user.id)
            .filter(Project.id == Environment.project_id)
            .all()
        )

    @classmethod
    def get(cls, environment_id):
        try:
            env = db.session.query(Environment).filter_by(id=environment_id).one()
        except NoResultFound:
            raise NotFoundError("environment")

        return env

    @classmethod
    def update_environment_role(cls, ids_and_roles, workspace_user):
        # TODO need to check permissions?
        for i in range(len(ids_and_roles)):
            new_role = ids_and_roles[i]["role"]
            environment = Environments.get(ids_and_roles[i]["id"])
            env_role = EnvironmentRole.get(
                workspace_user.user_id, ids_and_roles[i]["id"]
            )
            if env_role:
                env_role.role = new_role
            else:
                env_role = EnvironmentRole(
                    user=workspace_user.user, environment=environment, role=new_role
                )
            db.session.add(env_role)
            db.session.commit()
