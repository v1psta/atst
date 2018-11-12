from sqlalchemy import event, inspect
from flask import g
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import get_history

from atst.database import db
from atst.models.workspace_role import WorkspaceRole
from atst.models.audit_event import AuditEvent
from atst.utils import camel_to_snake, getattr_path

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"


class AuditableWorkspaceRole(AuditableMixin):
    target = target
    changed_state = get_changed_state()
    event_details = get_event_details()

    @classmethod
    def get_changed_state(self, resource):
        previous_state = {}
        inspr = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            history = getattr(inspr.attrs, attr.key).history
            if history.has_changes():
                previous_state[attr.key] = get_history(target, attr.key)[2].pop()

        from_role = previous_role["role"]
        to_role = target.role_displayname
        return {"role": [from_role, to_role]}

    @classmethod
    def get_event_details(self):
        # get user that is being updated
        # does this need to query the db?
        ws_role_id = target.auditable_request_id()
        ws_role = (
            db.session.query(WorkspaceRole)
            .filter(WorkspaceRole.id == ws_role_id)
            .first()
        )
        return {"user": ws_role.user_name}


class AuditableMixin(object):
    @staticmethod
    def create_audit_event(connection, resource, action):
        user_id = getattr_path(g, "current_user.id")
        workspace_id = resource.auditable_workspace_id()
        request_id = resource.auditable_request_id()
        resource_type = resource.auditable_resource_type()
        display_name = resource.auditable_displayname()
        changed_state = resource.auditable_changed_state()
        event_details = resource.auditable_event_details()

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
    def get_history(target):
        previous_state = {}
        inspr = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            history = getattr(inspr.attrs, attr.key).history
            if history.has_changes():
                previous_state[attr.key] = get_history(target, attr.key)[2].pop()
        return previous_state

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

    def auditable_changed_state(self):
        return getattr_path(self, "history")

    def auditable_event_details(self):
        return getattr_path(self, "auditable_event_details")

    def auditable_resource_type(self):
        return camel_to_snake(type(self).__name__)

    def auditable_workspace_id(self):
        return getattr_path(self, "workspace_id")

    def auditable_request_id(self):
        return getattr_path(self, "request_id")

    def auditable_displayname(self):
        return getattr_path(self, "displayname")
