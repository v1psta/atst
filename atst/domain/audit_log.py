from atst.domain.common import Query
from atst.models.audit_event import AuditEvent

class AuditEventQuery(Query):
    model = AuditEvent


class AuditLog(object):
    @classmethod
    def log_event(cls, user, resource, action):
        audit_event = AuditEventQuery.create(user=user, resource_id=resource.id, action=action)
        return AuditEventQuery.add_and_commit(audit_event)

    @classmethod
    def get_all_events(cls):
        return AuditEventQuery.get_all()
