from atst.database import db
from atst.models import EnvironmentRole, ApplicationRole


class EnvironmentRoles(object):
    @classmethod
    def create(cls, application_role, environment, role):
        env_role = EnvironmentRole(
            application_role=application_role, environment=environment, role=role
        )
        return env_role

    @classmethod
    def get(cls, application_role_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .filter(
                EnvironmentRole.application_role_id == application_role_id,
                EnvironmentRole.environment_id == environment_id,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def get_by_user_and_environment(cls, user_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .join(ApplicationRole)
            .filter(
                ApplicationRole.user_id == user_id,
                EnvironmentRole.environment_id == environment_id,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def delete(cls, application_role_id, environment_id):
        existing_env_role = EnvironmentRoles.get(application_role_id, environment_id)
        if existing_env_role:
            # TODO: Set status to pending_delete
            db.session.delete(existing_env_role)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def get_for_application_member(cls, application_role_id):
        return (
            db.session.query(EnvironmentRole)
            .filter(EnvironmentRole.application_role_id == application_role_id)
            .filter(EnvironmentRole.deleted != True)
            .all()
        )
