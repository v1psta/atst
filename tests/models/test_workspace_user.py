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
