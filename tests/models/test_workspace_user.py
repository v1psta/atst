from atst.domain.environments import Environments
from atst.domain.workspaces import Workspaces
from atst.domain.projects import Projects
from atst.domain.workspace_users import WorkspaceUsers
from atst.models.invitation import Status
from tests.factories import RequestFactory, UserFactory, InvitationFactory, WorkspaceRoleFactory


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
    workspace_user = Workspaces.create_member(owner, workspace, developer_data)

    assert not workspace_user.has_environment_roles


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
    workspace_user = Workspaces.create_member(owner, workspace, developer_data)
    project = Projects.create(
        owner, workspace, "my test project", "It's mine.", ["dev", "staging", "prod"]
    )
    Environments.add_member(project.environments[0], workspace_user.user, "developer")
    assert workspace_user.has_environment_roles


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
    workspace_user = Workspaces.create_member(owner, workspace, developer_data)

    assert workspace_user.role_displayname == "Developer"


def test_status_when_member_has_pending_invitation():
    workspace_role = WorkspaceRoleFactory.create(
        invitations=[InvitationFactory.create(status=Status.ACCEPTED)]
    )
    assert workspace_role.display_status == "Accepted"
