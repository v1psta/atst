from sqlalchemy import event, inspect
from flask import g

from atst.models.audit_event import AuditEvent
from atst.utils import camel_to_snake, getattr_path

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"


class AuditableMixin(object):
    @staticmethod
    def create_audit_event(connection, resource, action):
        user_id = getattr_path(g, "current_user.id")
        workspace_id = resource.auditable_workspace_id()
        request_id = resource.auditable_request_id()
        resource_type = resource.auditable_resource_type()
        display_name = resource.auditable_displayname()
        event_details = resource.auditable_event_details()

        changed_state = (
            resource.auditable_changed_state() if action == ACTION_UPDATE else None
        )

        audit_event = AuditEvent(
            user_id=user_id,
            workspace_id=workspace_id,
            request_id=request_id,
            resource_type=resource_type,
            resource_id=resource.id,
            display_name=display_name,
            action=action,
            changed_state=changed_state,
            event_details=event_details,
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
        if AuditableMixin.get_changes(target):
            target.create_audit_event(connection, target, ACTION_UPDATE)

    def get_changes(self):
        """
        This function returns a dictionary of the form {item: [from_value, to_value]},
        where 'item' is the attribute on the target that has been updated,
        'from_value' is the value of the attribute before it was updated,
        and 'to_value' is the current value of the attribute.

        There may be more than one item in the dictionary, but that is not expected.
        """
        previous_state = {}
        attrs = inspect(self).mapper.column_attrs
        for attr in attrs:
            history = getattr(inspect(self).attrs, attr.key).history
            if history.has_changes():
                deleted = history.deleted.pop() if history.deleted else None
                added = history.added.pop() if history.added else None
                previous_state[attr.key] = [deleted, added]
        return previous_state

    def auditable_changed_state(self):
        return getattr_path(self, "history")

    def auditable_event_details(self):
        return getattr_path(self, "event_details")

    def auditable_resource_type(self):
        return camel_to_snake(type(self).__name__)

    def auditable_workspace_id(self):
        return getattr_path(self, "workspace_id")

    def auditable_request_id(self):
        return getattr_path(self, "request_id")

    def auditable_displayname(self):
        return getattr_path(self, "displayname")
