from atst.database import db
from atst.domain.common import Query
from atst.domain.authz import Authorization, Permissions
from atst.models.audit_event import AuditEvent


class AuditEventQuery(Query):
    model = AuditEvent

    @classmethod
    def get_all(cls, pagination_opts):
        query = db.session.query(cls.model).order_by(cls.model.time_created.desc())
        return cls.paginate(query, pagination_opts)


class AuditLog(object):
    @classmethod
    def log_system_event(cls, resource, action):
        return cls._log(resource=resource, action=action)

    @classmethod
    def get_all_events(cls, user, pagination_opts=None):
        Authorization.check_atat_permission(
            user, Permissions.VIEW_AUDIT_LOG, "view audit log"
        )
        return AuditEventQuery.get_all(pagination_opts)

    @classmethod
    def get_by_resource(cls, resource_id):
        return db.session.query(AuditEvent).filter(AuditEvent.resource_id == resource_id).order_by(AuditEvent.time_created.desc()).all()

    @classmethod
    def _resource_type(cls, resource):
        return type(resource).__name__.lower()

    @classmethod
    def _log(cls, user=None, workspace_id=None, resource=None, action=None):
        resource_id = resource.id if resource else None
        resource_type = cls._resource_type(resource) if resource else None

        audit_event = AuditEventQuery.create(
            user=user,
            workspace_id=workspace_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
        )
        return AuditEventQuery.add_and_commit(audit_event)
