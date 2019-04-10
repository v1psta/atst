from atst.models import AuditEvent
from atst.domain.environments import Environments
from atst.domain.applications import Applications

from tests.factories import (
    PortfolioFactory,
    UserFactory,
    EnvironmentFactory,
    ApplicationFactory,
)


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = Applications.create(
        portfolio, "my test application", "It's mine.", ["dev", "staging", "prod"]
    )
    dev_environment = application.environments[0]

    dev_environment = Environments.add_member(dev_environment, developer, "developer")
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
