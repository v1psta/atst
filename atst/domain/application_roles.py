from atst.database import db
from atst.models.application_role import ApplicationRole
from atst.domain.permission_sets import PermissionSets


class ApplicationRoles(object):
    @classmethod
    def _permission_sets_for_names(cls, set_names):
        return PermissionSets.get_many(set_names)

    @classmethod
    def create(
        cls, user, application, permission_set_names=[PermissionSets.VIEW_APPLICATION]
    ):
        application_role = ApplicationRole(user=user, application_id=application.id)

        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            permission_set_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role
