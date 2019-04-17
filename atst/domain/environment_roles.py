from flask import current_app as app
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.exceptions import NotFoundError
from atst.models import EnvironmentRole, Environment, Application


class EnvironmentRoles(object):
    @classmethod
    def create(cls, user, environment, role):
        env_role = EnvironmentRole(user=user, environment=environment, role=role)
        if not user.cloud_id:
            user.cloud_id = app.csp.cloud.create_user(user)
        app.csp.cloud.create_role(env_role)
        return env_role

    @classmethod
    def get_for_portfolio(cls, user_id, environment_id, portfolio_id):
        try:
            return (
                db.session.query(EnvironmentRole)
                .join(Environment, EnvironmentRole.environment_id == Environment.id)
                .join(Application, Environment.application_id == Application.id)
                .filter(
                    EnvironmentRole.user_id == user_id,
                    EnvironmentRole.environment_id == environment_id,
                    Application.portfolio_id == portfolio_id,
                )
                .one()
            )
        except NoResultFound:
            raise NotFoundError("environment_role")

    @classmethod
    def get(cls, user_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .filter(
                EnvironmentRole.user_id == user_id,
                EnvironmentRole.environment_id == environment_id,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def delete(cls, user_id, environment_id):
        existing_env_role = EnvironmentRoles.get(user_id, environment_id)
        if existing_env_role:
            app.csp.cloud.delete_role(existing_env_role)
            db.session.delete(existing_env_role)
            db.session.commit()
            return True
        else:
            return False
