import pytest

from atst.models import AuditEvent
from atst.models.environment_role import CSPRole
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


@pytest.mark.parametrize(
    "env_data,expected_status",
    [
        [
            {"cloud_id": None, "root_user_info": None, "baseline_info": None},
            Environment.ProvisioningStatus.PENDING,
        ],
        [
            {"cloud_id": 1, "root_user_info": None, "baseline_info": None},
            Environment.ProvisioningStatus.PENDING,
        ],
        [
            {"cloud_id": 1, "root_user_info": {}, "baseline_info": None},
            Environment.ProvisioningStatus.PENDING,
        ],
        [
            {"cloud_id": 1, "root_user_info": {}, "baseline_info": {}},
            Environment.ProvisioningStatus.COMPLETED,
        ],
    ],
)
def test_environment_provisioning_status(env_data, expected_status):
    environment = EnvironmentFactory.create(**env_data)
    assert environment.provisioning_status == expected_status
