from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole, CSPRole
from atst.models.project import Project
from atst.domain.users import Users

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

    def get(cls, environment_id):
        try:
            env = db.session.query(Environment).filter_by(id=environment_id).one()
        except NoResultFound:
            raise NotFoundError("environment")

        return env

    @classmethod
    def update_environment_role(cls, environment_data, workspace_user):
        # TODO need to check permissions?
        new_role = environment_data["user_role_name"]
        environment = Environments.get(cls=cls, environment_id=environment_data["id"])
        if workspace_user.has_environment_roles:
            env_role = EnvironmentRole.get(workspace_user.user_id, environment.id)
            env_role.role = new_role
        else:
            env_role = EnvironmentRole(
                user=workspace_user.user,
                environment=environment,
                role=new_role
            )
        db.session.add(env_role)
        db.session.commit()
