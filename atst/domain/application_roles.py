from atst.database import db
from atst.models.application_role import ApplicationRole


class ApplicationRoles(object):
    @classmethod
    def create(cls, user, application, permission_sets):
        application_role = ApplicationRole(user=user, application_id=application.id)

        application_role.permission_sets = permission_sets

        db.session.add(application_role)
        db.session.commit()

        return application_role
