from flask import current_app as app
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole
from atst.models.project import Project
from atst.models.permissions import Permissions
from atst.domain.authz import Authorization
from atst.domain.environment_roles import EnvironmentRoles

from .exceptions import NotFoundError


class Environments(object):
    @classmethod
    def create(cls, project, name):
        environment = Environment(project=project, name=name)
        environment.cloud_id = app.csp.cloud.create_application(environment.name)
        return environment

    @classmethod
    def create_many(cls, project, names):
        environments = []
        for name in names:
            environment = Environments.create(project, name)
            environments.append(environment)

        db.session.add_all(environments)
        return environments

    @classmethod
    def add_member(cls, environment, user, role):
        environment_user = EnvironmentRole(
            user=user, environment=environment, role=role
        )
        db.session.add(environment_user)
        return environment

    @classmethod
    def for_user(cls, user, project):
        return (
            db.session.query(Environment)
            .join(EnvironmentRole)
            .join(Project)
            .filter(EnvironmentRole.user_id == user.id)
            .filter(Environment.project_id == project.id)
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
    def update_environment_roles(cls, user, workspace, workspace_role, ids_and_roles):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ADD_AND_ASSIGN_CSP_ROLES,
            "assign environment roles",
        )
        updated = False

        for id_and_role in ids_and_roles:
            new_role = id_and_role["role"]
            environment = Environments.get(id_and_role["id"])

            if new_role is None:
                role_deleted = EnvironmentRoles.delete(
                    workspace_role.user.id, environment.id
                )
                if role_deleted:
                    updated = True
            else:
                env_role = EnvironmentRoles.get(
                    workspace_role.user.id, id_and_role["id"]
                )
                if env_role and env_role.role != new_role:
                    env_role.role = new_role
                    updated = True
                    db.session.add(env_role)
                elif not env_role:
                    env_role = EnvironmentRole(
                        user=workspace_role.user, environment=environment, role=new_role
                    )
                    updated = True
                    db.session.add(env_role)

        if updated:
            db.session.commit()

        return updated

    @classmethod
    def revoke_access(cls, user, environment, target_user):
        Authorization.check_workspace_permission(
            user,
            environment.workspace,
            Permissions.REMOVE_CSP_ROLES,
            "revoke environment access",
        )
        EnvironmentRoles.delete(environment.id, target_user.id)
