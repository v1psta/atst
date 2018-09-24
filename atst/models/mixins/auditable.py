from sqlalchemy import event
from flask import g
import re

from atst.models.audit_event import AuditEvent

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"


def getattr_path(obj, path, default=None):
    _obj = obj
    for item in path.split("."):
        _obj = getattr(_obj, item, default)
    return _obj


def camel_to_snake(camel_cased):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_cased)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


class AuditableMixin(object):
    @staticmethod
    def create_audit_event(connection, resource, action):
        user_id = getattr_path(g, "current_user.id")
        workspace_id = resource.auditable_workspace_id()
        request_id = resource.auditable_request_id()
        resource_type = resource.auditable_resource_type()
        display_name = resource.auditable_displayname()

        audit_event = AuditEvent(
            user_id=user_id,
            workspace_id=workspace_id,
            request_id=request_id,
            resource_type=resource_type,
            resource_id=resource.id,
            display_name=display_name,
            action=action,
        )

        audit_event.save(connection)

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "after_insert", cls.audit_insert)
        event.listen(cls, "after_delete", cls.audit_delete)
        event.listen(cls, "after_update", cls.audit_update)

    @staticmethod
    def audit_insert(mapper, connection, target):
        """Listen for the `after_insert` event and create an AuditLog entry"""
        target.create_audit_event(connection, target, ACTION_CREATE)

    @staticmethod
    def audit_delete(mapper, connection, target):
        """Listen for the `after_delete` event and create an AuditLog entry"""
        target.create_audit_event(connection, target, ACTION_DELETE)

    @staticmethod
    def audit_update(mapper, connection, target):
        target.create_audit_event(connection, target, ACTION_UPDATE)

    def auditable_resource_type(self):
        return camel_to_snake(type(self).__name__)

    def auditable_workspace_id(self):
        return getattr_path(self, "workspace_id")

    def auditable_request_id(self):
        return getattr_path(self, "request_id")

    def auditable_displayname(self):
        return getattr_path(self, "displayname")
