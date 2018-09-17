from atst.database import db
from atst.domain.common import Query
from atst.domain.authz import Authorization, Permissions
from atst.models.audit_event import AuditEvent


class AuditEventQuery(Query):
    model = AuditEvent

    @classmethod
    def get_all(cls):
        return (
            db.session.query(AuditEvent).order_by(AuditEvent.time_created.desc()).all()
        )


class AuditLog(object):
    @classmethod
    def log_event(cls, user, resource, action):
        audit_event = AuditEventQuery.create(
            user=user,
            resource_id=resource.id,
            resource_name=cls._resource_name(resource),
            action=action,
        )
        return AuditEventQuery.add_and_commit(audit_event)

    @classmethod
    def log_system_event(cls, resource, action):
        audit_event = AuditEventQuery.create(
            resource_id=resource.id,
            resource_name=cls._resource_name(resource)
        )
        return AuditEventQuery.add_and_commit(audit_event)

    @classmethod
    def get_all_events(cls, user):
        Authorization.check_atat_permission(
            user, Permissions.VIEW_AUDIT_LOG, "view audit log"
        )
        return AuditEventQuery.get_all()

    @classmethod
    def _resource_name(cls, resource):
        return type(resource).__name__.lower()
