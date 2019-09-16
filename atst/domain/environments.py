from sqlalchemy import text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import load_only
from typing import List

from atst.database import db
from atst.models import Environment, Application, Portfolio, TaskOrder, CLIN
from atst.domain.environment_roles import EnvironmentRoles

from .exceptions import NotFoundError


class Environments(object):
    @classmethod
    def create(cls, user, application, name):
        environment = Environment(application=application, name=name, creator=user)
        db.session.add(environment)
        db.session.commit()
        return environment

    @classmethod
    def create_many(cls, user, application, names):
        environments = []
        for name in names:
            environment = Environments.create(user, application, name)
            environments.append(environment)

        db.session.add_all(environments)
        return environments

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
    def update_env_role(cls, environment, application_role, new_role):
        updated = False

        if new_role is None:
            updated = EnvironmentRoles.delete(application_role.id, environment.id)
        else:
            env_role = EnvironmentRoles.get(application_role.id, environment.id)
            if env_role and env_role.role != new_role:
                env_role.role = new_role
                updated = True
                db.session.add(env_role)
            elif not env_role:
                env_role = EnvironmentRoles.create(
                    application_role=application_role,
                    environment=environment,
                    role=new_role,
                )
                updated = True
                db.session.add(env_role)

        if updated:
            db.session.commit()

        return updated

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

        # TODO: How do we work around environment deletion being a largely manual process in the CSPs

        return environment

    @classmethod
    def base_provision_query(cls, now):
        return (
            db.session.query(Environment)
            .join(Application)
            .join(Portfolio)
            .join(TaskOrder)
            .join(CLIN)
            .filter(CLIN.start_date <= now)
            .filter(CLIN.end_date > now)
            # select only these columns
            .options(load_only("id", "creator_id"))
        )

    @classmethod
    def get_environments_pending_creation(cls, now) -> List[Environment]:
        """
        Any environment with an active CLIN that doesn't yet have a `cloud_id`.
        """
        return cls.base_provision_query(now).filter(Environment.cloud_id == None).all()

    @classmethod
    def get_environments_pending_atat_user_creation(cls, now) -> List[Environment]:
        """
        Any environment with an active CLIN that has a cloud_id but no `root_user_info`.
        """
        return (
            cls.base_provision_query(now)
            .filter(Environment.cloud_id != None)
            .filter(Environment.root_user_info == text("'null'"))
        ).all()

    @classmethod
    def get_environments_pending_baseline_creation(cls, now) -> List[Environment]:
        """
        Any environment with an active CLIN that has a `cloud_id` and `root_user_info`
        but no `baseline_info`.
        """
        return (
            cls.base_provision_query(now)
            .filter(Environment.cloud_id != None)
            .filter(Environment.root_user_info != text("'null'"))
            .filter(Environment.baseline_info == text("'null'"))
        ).all()
