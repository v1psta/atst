import ctypes
import sqlalchemy
from sqlalchemy import or_, event as sqlalchemy_event

from atst.database import db
from atst.app import make_config, make_app

from atst.models.audit_event import AuditEvent
from atst.models.environment import Environment
from atst.models.environment_role import EnvironmentRole
from atst.models.project import Project
from atst.models.request import Request
from atst.models.request_revision import RequestRevision
from atst.models.request_status_event import RequestStatusEvent
from atst.models.role import Role
from atst.models.user import User
from atst.models.workspace_role import WorkspaceRole
from atst.models.workspace import Workspace
from atst.models.mixins import AuditableMixin


dod_ids = [
    "1234567890",
    "2345678901",
    "3456789012",
    "4567890123",
    "5678901234",
    "6789012345",
    "2342342342",
    "3453453453",
    "4564564564",
    "6786786786",
]


def remove_sample_data():
    users = db.session.query(User).filter(User.dod_id.in_(dod_ids)).all()

    delete_listeners = [
        k
        for k in sqlalchemy_event.registry._key_to_collection
        if k[1] == "after_delete"
    ]
    for listener in delete_listeners:
        [class_id, identifier, _] = listener
        model = ctypes.cast(class_id, ctypes.py_object).value
        sqlalchemy_event.remove(model, identifier, AuditableMixin.audit_delete)

    for user in users:
        requests = (
            db.session.query(Request)
            .filter(Request.id.in_([r.id for r in user.owned_requests]))
            .all()
        )
        request_audit = (
            db.session.query(AuditEvent)
            .filter(AuditEvent.request_id.in_([r.id for r in requests]))
            .all()
        )
        request_audit = (
            db.session.query(AuditEvent)
            .filter(AuditEvent.request_id.in_([r.id for r in requests]))
            .all()
        )
        events = [ev for r in requests for ev in r.status_events]
        revisions = [rev for r in requests for rev in r.revisions]
        workspaces = [r.workspace for r in requests if r.workspace]
        ws_audit = (
            db.session.query(AuditEvent)
            .filter(AuditEvent.workspace_id.in_([w.id for w in workspaces]))
            .all()
        )
        workspace_roles = [role for workspace in workspaces for role in workspace.roles]
        projects = [p for workspace in workspaces for p in workspace.projects]
        environments = (
            db.session.query(Environment)
            .filter(Environment.project_id.in_([p.id for p in projects]))
            .all()
        )
        roles = [role for env in environments for role in env.roles]

        for set_of_things in [
            roles,
            environments,
            projects,
            workspace_roles,
            ws_audit,
            events,
            revisions,
            request_audit,
        ]:
            for thing in set_of_things:
                db.session.delete(thing)

        db.session.commit()

        query = "DELETE FROM workspaces WHERE workspaces.id = ANY(:ids);"
        db.session.connection().execute(
            sqlalchemy.text(query), ids=[w.id for w in workspaces]
        )

        query = "DELETE FROM requests WHERE requests.id = ANY(:ids);"
        db.session.connection().execute(
            sqlalchemy.text(query), ids=[r.id for r in requests]
        )

        db.session.commit()


if __name__ == "__main__":
    config = make_config()
    app = make_app(config)
    with app.app_context():
        remove_sample_data()
