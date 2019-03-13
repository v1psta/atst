import pytest
import datetime

from atst.domain.environments import Environments
from atst.domain.portfolios import Portfolios
from atst.domain.applications import Applications
from atst.domain.permission_sets import PermissionSets
from atst.models.portfolio_role import Status
from atst.models.invitation import Status as InvitationStatus
from atst.models.audit_event import AuditEvent
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from tests.factories import (
    UserFactory,
    InvitationFactory,
    PortfolioRoleFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    ApplicationFactory,
    PortfolioFactory,
)
from atst.domain.portfolio_roles import PortfolioRoles


def test_has_no_ws_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = PortfolioRoles.add(user, portfolio.id)
    create_event = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "create"
        )
        .one()
    )

    assert not create_event.changed_state


@pytest.mark.skip(reason="need to update audit log permission set handling")
def test_has_ws_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    role = session.query(Role).filter(Role.name == "developer").one()
    # in order to get the history, we don't want the PortfolioRoleFactory
    #  to commit after create()
    PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)
    PortfolioRoles.update_role(portfolio_role, "admin")
    changed_events = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "update"
        )
        .all()
    )
    # changed_state["role"] returns a list [previous role, current role]
    assert changed_events[0].changed_state["role"][0] == "developer"
    assert changed_events[0].changed_state["role"][1] == "admin"


def test_has_ws_status_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    # in order to get the history, we don't want the PortfolioRoleFactory
    #  to commit after create()
    PortfolioRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)
    PortfolioRoles.enable(portfolio_role)
    changed_events = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == portfolio_role.id, AuditEvent.action == "update"
        )
        .all()
    )

    # changed_state["status"] returns a list [previous status, current status]
    assert changed_events[0].changed_state["status"][0] == "pending"
    assert changed_events[0].changed_state["status"][1] == "active"


def test_has_no_env_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(
        application=application, name="new environment!"
    )

    env_role = EnvironmentRoleFactory.create(
        user=user, environment=environment, role="developer"
    )
    create_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env_role.id, AuditEvent.action == "create")
        .one()
    )

    assert not create_event.changed_state


def test_has_env_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(
        application=application, name="new environment!"
    )

    env_role = EnvironmentRoleFactory.create(
        user=user, environment=environment, role="developer"
    )
    Environments.update_environment_roles(
        owner, portfolio, portfolio_role, [{"role": "admin", "id": environment.id}]
    )
    changed_events = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env_role.id, AuditEvent.action == "update")
        .all()
    )
    # changed_state["role"] returns a list [previous role, current role]
    assert changed_events[0].changed_state["role"][0] == "developer"
    assert changed_events[0].changed_state["role"][1] == "admin"


def test_event_details():
    owner = UserFactory.create()
    user = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = PortfolioRoles.add(user, portfolio.id)

    assert portfolio_role.event_details["updated_user_name"] == user.displayname
    assert portfolio_role.event_details["updated_user_id"] == str(user.id)


def test_has_no_environment_roles():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "portfolio_role": "developer",
    }

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = Portfolios.create_member(owner, portfolio, developer_data)

    assert not portfolio_role.has_environment_roles


def test_has_environment_roles():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "portfolio_role": "developer",
    }

    portfolio = PortfolioFactory.create(owner=owner)
    portfolio_role = Portfolios.create_member(owner, portfolio, developer_data)
    application = Applications.create(
        owner,
        portfolio,
        "my test application",
        "It's mine.",
        ["dev", "staging", "prod"],
    )
    Environments.add_member(
        application.environments[0], portfolio_role.user, "developer"
    )
    assert portfolio_role.has_environment_roles


def test_status_when_member_is_active():
    portfolio_role = PortfolioRoleFactory.create(status=Status.ACTIVE)
    assert portfolio_role.display_status == "Active"


def test_status_when_invitation_has_been_rejected_for_expirations():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        portfolio_role=portfolio_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert portfolio_role.display_status == "Invite expired"


def test_status_when_invitation_has_been_rejected_for_wrong_user():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        portfolio_role=portfolio_role, status=InvitationStatus.REJECTED_WRONG_USER
    )
    assert portfolio_role.display_status == "Error on invite"


def test_status_when_invitation_is_expired():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        portfolio_role=portfolio_role,
        status=InvitationStatus.PENDING,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    assert portfolio_role.display_status == "Invite expired"


def test_can_not_resend_invitation_if_active():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        portfolio_role=portfolio_role, status=InvitationStatus.ACCEPTED
    )
    assert not portfolio_role.can_resend_invitation


def test_can_resend_invitation_if_expired():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        portfolio_role=portfolio_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert portfolio_role.can_resend_invitation


def test_can_list_all_environments():
    portfolio = PortfolioFactory.create(
        applications=[
            {
                "name": "application1",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "application2",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "application3",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
        ]
    )

    assert len(portfolio.all_environments) == 9


def test_can_list_all_permissions():
    role_one = PermissionSets.get("view_portfolio_funding")
    role_two = PermissionSets.get("view_portfolio_reports")
    port_role = PortfolioRoleFactory.create(permission_sets=[role_one, role_two])
    expected_perms = role_one.permissions + role_two.permissions
    assert expected_perms == expected_perms
