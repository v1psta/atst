from flask import current_app as app
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole
from atst.models.application import Application
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.users import Users

from .exceptions import NotFoundError


class Environments(object):
    @classmethod
    def create(cls, application, name):
        environment = Environment(application=application, name=name)
        environment.cloud_id = app.csp.cloud.create_application(environment.name)
        db.session.add(environment)
        db.session.commit()
        return environment

    @classmethod
    def create_many(cls, application, names):
        environments = []
        for name in names:
            environment = Environments.create(application, name)
            environments.append(environment)

        db.session.add_all(environments)
        return environments

    @classmethod
    def add_member(cls, environment, user, role):
        environment_user = EnvironmentRoles.create(
            user=user, environment=environment, role=role
        )
        db.session.add(environment_user)
        return environment

    @classmethod
    def for_user(cls, user, application):
        return (
            db.session.query(Environment)
            .join(EnvironmentRole)
            .join(Application)
            .filter(EnvironmentRole.user_id == user.id)
            .filter(Environment.application_id == application.id)
            .all()
        )

    @classmethod
    def update(cls, environment, name=None):
        if name is not None:
            environment.name = name
            db.session.add(environment)
            db.session.commit()

    @classmethod
    def get(cls, environment_id):
        try:
            env = (
                db.session.query(Environment)
                .filter_by(id=environment_id, deleted=False)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("environment")

        return env

    @classmethod
    def update_env_role(cls, environment, user, new_role):
        updated = False

        if new_role is None:
            updated = EnvironmentRoles.delete(user.id, environment.id)
        else:
            env_role = EnvironmentRoles.get(user.id, environment.id)
            if env_role and env_role.role != new_role:
                env_role.role = new_role
                updated = True
                db.session.add(env_role)
            elif not env_role:
                env_role = EnvironmentRoles.create(
                    user=user, environment=environment, role=new_role
                )
                updated = True
                db.session.add(env_role)

        if updated:
            db.session.commit()

        return updated

    @classmethod
    def update_env_roles_by_environment(cls, environment_id, team_roles):
        environment = Environments.get(environment_id)

        for member in team_roles:
            new_role = member["role_name"]
            user = Users.get(member["user_id"])
            Environments.update_env_role(
                environment=environment, user=user, new_role=new_role
            )

    @classmethod
    def update_env_roles_by_member(cls, member, env_roles):
        for env_roles in env_roles:
            new_role = env_roles["role"]
            environment = Environments.get(env_roles["id"])
            Environments.update_env_role(
                environment=environment, user=member, new_role=new_role
            )

    @classmethod
    def revoke_access(cls, environment, target_user):
        EnvironmentRoles.delete(environment.id, target_user.id)

    @classmethod
    def delete(cls, environment, commit=False):
        environment.deleted = True
        db.session.add(environment)

        for role in environment.roles:
            role.deleted = True
            db.session.add(role)

        if commit:
            db.session.commit()

        app.csp.cloud.delete_application(environment.cloud_id)

        return environment
