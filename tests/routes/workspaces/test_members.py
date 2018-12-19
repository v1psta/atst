from flask import url_for

from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceRoleFactory,
    InvitationFactory,
)
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_roles import WorkspaceRoles
from atst.domain.projects import Projects
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.queue import queue
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from atst.models.invitation import Status as InvitationStatus


def create_workspace_and_invite_user(
    ws_role="developer",
    ws_status=WorkspaceRoleStatus.PENDING,
    invite_status=InvitationStatus.PENDING,
):
    workspace = WorkspaceFactory.create()
    if ws_role != "owner":
        user = UserFactory.create()
        member = WorkspaceRoleFactory.create(
            user=user, workspace=workspace, status=ws_status
        )
        InvitationFactory.create(
            user=workspace.owner,
            workspace_role=member,
            email=member.user.email,
            status=invite_status,
        )
    return workspace


def test_user_with_permission_has_add_member_link(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
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


def test_permissions_for_view_member(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    user_session(user)
    response = client.get(
        url_for("workspaces.view_member", workspace_id=workspace.id, member_id=user.id)
    )
    assert response.status_code == 404


def test_create_member(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    queue_length = len(queue.get_queue())

    response = client.post(
        url_for("workspaces.create_member", workspace_id=workspace.id),
        data={
            "dod_id": user.dod_id,
            "first_name": "Wilbur",
            "last_name": "Zuckerman",
            "email": "some_pig@zuckermans.com",
            "workspace_role": "developer",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert user.has_workspaces
    assert user.invitations
    assert len(queue.get_queue()) == queue_length + 1


def test_view_member_shows_role(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    user_session(workspace.owner)
    response = client.get(
        url_for("workspaces.view_member", workspace_id=workspace.id, member_id=user.id)
    )
    assert response.status_code == 200
    assert "initial-choice='developer'".encode() in response.data


def test_update_member_workspace_role(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={"workspace_role": "security_auditor"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"role updated successfully" in response.data
    assert member.role_name == "security_auditor"


def test_update_member_workspace_role_with_no_data(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert member.role_name == "developer"


def test_update_member_environment_role(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    project = Projects.create(
        workspace.owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1", "env2"},
    )
    env1_id = project.environments[0].id
    env2_id = project.environments[1].id
    for env in project.environments:
        Environments.add_member(env, user, "developer")
    user_session(workspace.owner)
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
    assert b"role updated successfully" not in response.data
    assert b"access successfully changed" in response.data
    assert EnvironmentRoles.get(user.id, env1_id).role == "security_auditor"
    assert EnvironmentRoles.get(user.id, env2_id).role == "devops"


def test_update_member_environment_role_with_no_data(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceRoles.add(user, workspace.id, "developer")
    project = Projects.create(
        workspace.owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1"},
    )
    env1_id = project.environments[0].id
    for env in project.environments:
        Environments.add_member(env, user, "developer")
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={"env_" + str(env1_id): None, "env_" + str(env1_id): ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"access successfully changed" not in response.data
    assert EnvironmentRoles.get(user.id, env1_id).role == "developer"


def test_revoke_active_member_access(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.ACTIVE
    )
    Projects.create(
        workspace.owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1"},
    )
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.revoke_access", workspace_id=workspace.id, member_id=member.id
        )
    )
    assert response.status_code == 302
    assert WorkspaceRoles.get_by_id(member.id).num_environment_roles == 0


def test_does_not_show_any_buttons_if_owner(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.get(
        url_for(
            "workspaces.view_member",
            workspace_id=workspace.id,
            member_id=workspace.owner.id,
        )
    )
    assert "Remove Workspace Access" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()


def test_only_shows_revoke_access_button_if_active(client, user_session):
    workspace = create_workspace_and_invite_user(
        ws_status=WorkspaceRoleStatus.ACTIVE, invite_status=InvitationStatus.ACCEPTED
    )
    user_session(workspace.owner)
    member = workspace.members[1]
    response = client.get(
        url_for(
            "workspaces.view_member",
            workspace_id=workspace.id,
            member_id=member.user.id,
        )
    )
    assert "Remove Workspace Access" in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()


def test_only_shows_revoke_invite_button_if_pending(client, user_session):
    workspace = create_workspace_and_invite_user(
        ws_status=WorkspaceRoleStatus.PENDING, invite_status=InvitationStatus.PENDING
    )
    user_session(workspace.owner)
    member = workspace.members[1]
    response = client.get(
        url_for(
            "workspaces.view_member",
            workspace_id=workspace.id,
            member_id=member.user.id,
        )
    )
    assert "Revoke Invitation" in response.data.decode()
    assert "Remove Workspace Access" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()


def test_only_shows_resend_button_if_expired(client, user_session):
    workspace = create_workspace_and_invite_user(
        ws_status=WorkspaceRoleStatus.PENDING,
        invite_status=InvitationStatus.REJECTED_EXPIRED,
    )
    user_session(workspace.owner)
    member = workspace.members[1]
    response = client.get(
        url_for(
            "workspaces.view_member",
            workspace_id=workspace.id,
            member_id=member.user.id,
        )
    )
    assert "Resend Invitation" in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
    assert "Remove Workspace Access" not in response.data.decode()


def test_only_shows_resend_button_if_revoked(client, user_session):
    workspace = create_workspace_and_invite_user(
        ws_status=WorkspaceRoleStatus.PENDING, invite_status=InvitationStatus.REVOKED
    )
    user_session(workspace.owner)
    member = workspace.members[1]
    response = client.get(
        url_for(
            "workspaces.view_member",
            workspace_id=workspace.id,
            member_id=member.user.id,
        )
    )
    assert "Resend Invitation" in response.data.decode()
    assert "Remove Workspace Access" not in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
