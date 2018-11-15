import datetime

from atst.domain.environments import Environments
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from atst.domain.workspace_roles import WorkspaceRoles
from atst.models.workspace_role import Status
from atst.models.invitation import Status as InvitationStatus
from tests.factories import (
    RequestFactory,
    UserFactory,
    InvitationFactory,
    WorkspaceRoleFactory,
)


def test_has_no_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = WorkspaceRoles.add(user, workspace.id, "developer")
    create_event = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == workspace_role.id, AuditEvent.action == "create"
        )
        .one()
    )

    assert not create_event.changed_state


def test_has_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = WorkspaceRoles.add(user, workspace.id, "developer")
    WorkspaceRoles.update_role(workspace_role, "admin")
    changed_events = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == workspace_role.id, AuditEvent.changed_state != None)
        .all()
    )

    # changed_state["role"] returns a list [previous role, current role]
    assert changed_events[0].changed_state["role"][0] == 'developer'
    assert changed_events[0].changed_state["role"][1] == 'admin'


def test_has_status_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = WorkspaceRoles.add(user, workspace.id, "developer")
    session.add(workspace_role)
    session.commit()
    workspace_role.status = Status.ACTIVE
    session.add(workspace_role)
    session.commit()
    audit_events = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == workspace_role.id)
        .all()
    )
    changed_events = [event for event in audit_events if event.changed_state]

    import ipdb; ipdb.set_trace()

    assert changed_events[0].changed_state["status"][0]
    assert changed_events[0].changed_state["status"][1]


def test_event_details():
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = WorkspaceRoles.add(user, workspace.id, "developer")

    assert workspace_role.event_details["updated_user_name"] == user.displayname
    assert workspace_role.event_details["updated_user_id"] == str(user.id)


def test_has_no_environment_roles():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "workspace_role": "developer",
    }

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = Workspaces.create_member(owner, workspace, developer_data)

    assert not workspace_role.has_environment_roles


def test_has_environment_roles():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "workspace_role": "developer",
    }

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = Workspaces.create_member(owner, workspace, developer_data)
    project = Projects.create(
        owner, workspace, "my test project", "It's mine.", ["dev", "staging", "prod"]
    )
    Environments.add_member(project.environments[0], workspace_role.user, "developer")
    assert workspace_role.has_environment_roles


def test_role_displayname():
    owner = UserFactory.create()
    developer_data = {
        "dod_id": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@mail.com",
        "workspace_role": "developer",
    }

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = Workspaces.create_member(owner, workspace, developer_data)

    assert workspace_role.role_displayname == "Developer"


def test_status_when_member_is_active():
    workspace_role = WorkspaceRoleFactory.create(status=Status.ACTIVE)
    assert workspace_role.display_status == "Active"


def test_status_when_invitation_has_been_rejected_for_expirations():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[InvitationFactory.create(status=InvitationStatus.REJECTED_EXPIRED)]
    )
    assert workspace_role.display_status == "Invite expired"


def test_status_when_invitation_has_been_rejected_for_wrong_user():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[
            InvitationFactory.create(status=InvitationStatus.REJECTED_WRONG_USER)
        ]
    )
    assert workspace_role.display_status == "Error on invite"


def test_status_when_invitation_is_expired():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[
            InvitationFactory.create(
                status=InvitationStatus.PENDING,
                expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
            )
        ]
    )
    assert workspace_role.display_status == "Invite expired"


def test_can_not_resend_invitation_if_active():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[InvitationFactory.create(status=InvitationStatus.ACCEPTED)]
    )
    assert not workspace_role.can_resend_invitation


def test_can_resend_invitation_if_expired():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[InvitationFactory.create(status=InvitationStatus.REJECTED_EXPIRED)]
    )
    assert workspace_role.can_resend_invitation
