from sqlalchemy import event, inspect
from flask import g
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import get_history

from atst.models.audit_event import AuditEvent
from atst.utils import camel_to_snake, getattr_path

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"


class AuditableMixin(object):
    @staticmethod
    def create_audit_event(connection, resource, action, previous_state=None):
        user_id = getattr_path(g, "current_user.id")
        workspace_id = resource.auditable_workspace_id()
        request_id = resource.auditable_request_id()
        resource_type = resource.auditable_resource_type()
        display_name = resource.auditable_displayname()
        previous_role_id = previous_state["role_id"]

        audit_event = AuditEvent(
            user_id=user_id,
            workspace_id=workspace_id,
            request_id=request_id,
            resource_type=resource_type,
            resource_id=resource.id,
            display_name=display_name,
            action=action,
            previous_role_id=previous_role_id,
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
        previous_state = {}
        inspr = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            history = getattr(inspr.attrs, attr.key).history
            if history.has_changes():
                previous_state[attr.key] = get_history(target, attr.key)[2].pop()
        target.create_audit_event(connection, target, ACTION_UPDATE, previous_state)

    def auditable_resource_type(self):
        return camel_to_snake(type(self).__name__)

    def auditable_workspace_id(self):
        return getattr_path(self, "workspace_id")

    def auditable_request_id(self):
        return getattr_path(self, "request_id")

    def auditable_displayname(self):
        return getattr_path(self, "displayname")
