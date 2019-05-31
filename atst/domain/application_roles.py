from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models import ApplicationRole, ApplicationRoleStatus
from .permission_sets import PermissionSets
from .exceptions import NotFoundError


class ApplicationRoles(object):
    @classmethod
    def _permission_sets_for_names(cls, set_names):
        set_names = set(set_names).union({PermissionSets.VIEW_APPLICATION})
        return PermissionSets.get_many(set_names)

    @classmethod
    def create(cls, user, application, permission_set_names):
        application_role = ApplicationRole(
            user=user, application_id=application.id, application=application
        )

        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            permission_set_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role

    @classmethod
    def enable(cls, role, user):
        role.status = ApplicationRoleStatus.ACTIVE
        role.user = user

        db.session.add(role)
        db.session.commit()

    @classmethod
    def get(cls, user_id, application_id):
        try:
            app_role = (
                db.session.query(ApplicationRole)
                .filter_by(user_id=user_id, application_id=application_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("application_role")

        return app_role

    @classmethod
    def get_by_id(cls, id_):
        try:
            return (
                db.session.query(ApplicationRole)
                .filter(ApplicationRole.id == id_)
                .filter(ApplicationRole.status != ApplicationRoleStatus.DISABLED)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("application_role")

    @classmethod
    def update_permission_sets(cls, application_role, new_perm_sets_names):
        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            new_perm_sets_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role
