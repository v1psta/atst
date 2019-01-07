from flask import current_app as app

from atst.models.environment_role import EnvironmentRole
from atst.database import db


class EnvironmentRoles(object):
    @classmethod
    def create(cls, user, environment, role):
        env_role = EnvironmentRole(user=user, environment=environment, role=role)
        app.csp.cloud.create_role(env_role)
        return env_role

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
