from flask import url_for

from tests.factories import UserFactory, WorkspaceFactory
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.projects import Projects
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.models.workspace_user import WorkspaceUser


def test_user_with_permission_has_add_project_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "owner")

    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_project_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/projects/new"'.format(workspace.id).encode()
        not in response.data
    )


def test_user_with_permission_has_add_member_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "owner")

    user_session(user)
    response = client.get("/workspaces/{}/members".format(workspace.id))
    assert (
        'href="/workspaces/{}/members/new"'.format(workspace.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_member_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    user_session(user)
    response = client.get("/workspaces/{}/members".format(workspace.id))
    assert (
        'href="/workspaces/{}/members/new"'.format(workspace.id).encode()
        not in response.data
    )


def test_update_workspace_name(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "admin")
    user_session(user)
    response = client.post(
        url_for("workspaces.edit_workspace", workspace_id=workspace.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert workspace.name == "a cool new name"


def test_update_member_workspace_role(client, user_session):
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(owner, workspace, "admin")
    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
    user_session(owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={"workspace_role": "security_auditor"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert member.role == "security_auditor"


def test_update_member_environment_role(client, user_session):
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(owner, workspace, "admin")

    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
    project = Projects.create(
        owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1", "env2"},
    )
    env1_id = project.environments[0].id
    env2_id = project.environments[1].id
    for env in project.environments:
        Environments.add_member(owner, env, user, "developer")
    user_session(owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={
            "workspace_role": "developer",
            "env_" + str(env1_id): "security_auditor",
            "env_" + str(env2_id): "devops",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert EnvironmentRoles.get(user.id, env1_id).role == "security_auditor"
    assert EnvironmentRoles.get(user.id, env2_id).role == "devops"
