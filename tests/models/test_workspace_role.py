import datetime

from atst.domain.environments import Environments
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from atst.models.workspace_role import Status
from atst.models.role import Role
from atst.models.invitation import Status as InvitationStatus
from atst.models.audit_event import AuditEvent
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from tests.factories import (
    RequestFactory,
    UserFactory,
    InvitationFactory,
    WorkspaceRoleFactory,
    EnvironmentFactory,
    EnvironmentRoleFactory,
    ProjectFactory,
    WorkspaceFactory,
)
from atst.domain.workspace_roles import WorkspaceRoles


def test_has_no_ws_role_history(session):
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


def test_has_ws_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    role = session.query(Role).filter(Role.name == "developer").one()
    # in order to get the history, we don't want the WorkspaceRoleFactory
    #  to commit after create()
    WorkspaceRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, role=role
    )
    WorkspaceRoles.update_role(workspace_role, "admin")
    changed_events = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == workspace_role.id, AuditEvent.action == "update"
        )
        .all()
    )
    # changed_state["role"] returns a list [previous role, current role]
    assert changed_events[0].changed_state["role"][0] == "developer"
    assert changed_events[0].changed_state["role"][1] == "admin"


def test_has_ws_status_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()

    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    # in order to get the history, we don't want the WorkspaceRoleFactory
    #  to commit after create()
    WorkspaceRoleFactory._meta.sqlalchemy_session_persistence = "flush"
    workspace_role = WorkspaceRoleFactory.create(workspace=workspace, user=user)
    WorkspaceRoles.enable(workspace_role)
    changed_events = (
        session.query(AuditEvent)
        .filter(
            AuditEvent.resource_id == workspace_role.id, AuditEvent.action == "update"
        )
        .all()
    )

    # changed_state["status"] returns a list [previous status, current status]
    assert changed_events[0].changed_state["status"][0] == "pending"
    assert changed_events[0].changed_state["status"][1] == "active"


def test_has_no_env_role_history(session):
    owner = UserFactory.create()
    user = UserFactory.create()
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    project = ProjectFactory.create(workspace=workspace)
    environment = EnvironmentFactory.create(project=project, name="new environment!")

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
    workspace = Workspaces.create(RequestFactory.create(creator=owner))
    workspace_role = WorkspaceRoleFactory.create(workspace=workspace, user=user)
    project = ProjectFactory.create(workspace=workspace)
    environment = EnvironmentFactory.create(project=project, name="new environment!")

    env_role = EnvironmentRoleFactory.create(
        user=user, environment=environment, role="developer"
    )
    Environments.update_environment_roles(
        owner, workspace, workspace_role, [{"role": "admin", "id": environment.id}]
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
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        workspace_role=workspace_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert workspace_role.display_status == "Invite expired"


def test_status_when_invitation_has_been_rejected_for_wrong_user():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        workspace_role=workspace_role, status=InvitationStatus.REJECTED_WRONG_USER
    )
    assert workspace_role.display_status == "Error on invite"


def test_status_when_invitation_is_expired():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        workspace_role=workspace_role,
        status=InvitationStatus.PENDING,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    assert workspace_role.display_status == "Invite expired"


def test_can_not_resend_invitation_if_active():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        workspace_role=workspace_role, status=InvitationStatus.ACCEPTED
    )
    assert not workspace_role.can_resend_invitation


def test_can_resend_invitation_if_expired():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    workspace_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invitation = InvitationFactory.create(
        workspace_role=workspace_role, status=InvitationStatus.REJECTED_EXPIRED
    )
    assert workspace_role.can_resend_invitation


def test_can_list_all_environments():
    workspace = WorkspaceFactory.create(
        projects=[
            {
                "name": "project1",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "project2",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
            {
                "name": "project3",
                "environments": [
                    {"name": "dev"},
                    {"name": "staging"},
                    {"name": "prod"},
                ],
            },
        ]
    )

    assert len(workspace.all_environments) == 9
