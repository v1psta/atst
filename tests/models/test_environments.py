from atst.models import AuditEvent
from atst.models.environment_role import CSPRole
from atst.domain.environments import Environments
from atst.domain.applications import Applications

from tests.factories import *


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "my test application",
        "It's mine.",
        ["dev", "staging", "prod"],
    )
    dev_environment = application.environments[0]

    application_role = ApplicationRoleFactory.create(
        user=developer, application=application
    )
    EnvironmentRoleFactory.create(
        application_role=application_role,
        environment=dev_environment,
        role=CSPRole.BASIC_ACCESS.value,
    )
    assert developer in dev_environment.users


def test_audit_event_for_environment_deletion(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env.deleted = True
    session.add(env)
    session.commit()

    update_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env.id, AuditEvent.action == "update")
        .one()
    )
    assert update_event.changed_state.get("deleted")
    before, after = update_event.changed_state["deleted"]
    assert not before
    assert after
