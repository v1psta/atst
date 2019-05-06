from atst.database import db
from atst.models import ApplicationRole, ApplicationRoleStatus
from atst.domain.permission_sets import PermissionSets


class ApplicationRoles(object):
    @classmethod
    def _permission_sets_for_names(cls, set_names):
        set_names = set(set_names).union({PermissionSets.VIEW_APPLICATION})
        return PermissionSets.get_many(set_names)

    @classmethod
    def create(cls, user, application, permission_set_names):
        application_role = ApplicationRole(user=user, application_id=application.id)

        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            permission_set_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role

    @classmethod
    def enable(cls, role):
        role.status = ApplicationRoleStatus.ACTIVE

        db.session.add(role)
        db.session.commit()
