from atst.database import db
from atst.domain.common import Query
from atst.domain.authz import Authorization, Permissions
from atst.models.audit_event import AuditEvent


class AuditEventQuery(Query):
    model = AuditEvent

    @classmethod
    def get_all(cls):
        return db.session.query(cls.model).order_by(cls.model.time_created.desc()).all()


class AuditLog(object):
    @classmethod
    def get_all_events(cls, user):
        Authorization.check_atat_permission(
            user, Permissions.VIEW_AUDIT_LOG, "view audit log"
        )
        return AuditEventQuery.get_all()

