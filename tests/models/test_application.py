from atst.models import AuditEvent

from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    EnvironmentFactory,
)


def test_application_num_users():
    application = ApplicationFactory.create(
        environments=[{"name": "dev"}, {"name": "staging"}, {"name": "prod"}]
    )
    assert application.num_users == 0

    ApplicationRoleFactory.create(application=application)
    assert application.num_users == 1


def test_application_environments_excludes_deleted():
    app = ApplicationFactory.create()
    env = EnvironmentFactory.create(application=app)
    EnvironmentFactory.create(application=app, deleted=True)
    assert len(app.environments) == 1
    assert app.environments[0].id == env.id


def test_audit_event_for_application_deletion(session):
    app = ApplicationFactory.create()
    app.deleted = True
    session.add(app)
    session.commit()

    update_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == app.id, AuditEvent.action == "update")
        .one()
    )
    assert update_event.changed_state.get("deleted")
    assert update_event.changed_state["deleted"] == [False, True]
