import datetime
from flask import url_for

from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceRoleFactory,
    InvitationFactory,
)
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_users import WorkspaceUsers
from atst.domain.projects import Projects
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.models.workspace_user import WorkspaceUser
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from atst.models.invitation import Status as InvitationStatus
from atst.queue import queue
from atst.domain.users import Users


def test_user_with_permission_has_budget_report_link(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/reports"'.format(workspace.id).encode() in response.data
    )


def test_user_without_permission_has_no_budget_report_link(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(
        user, workspace, "developer", status=WorkspaceRoleStatus.ACTIVE
    )
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert (
        'href="/workspaces/{}/reports"'.format(workspace.id).encode()
        not in response.data
    )


def test_user_with_permission_has_add_project_link(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
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


def test_update_workspace_name(client, user_session):
    workspace = WorkspaceFactory.create()
    user_session(workspace.owner)
    response = client.post(
        url_for("workspaces.edit_workspace", workspace_id=workspace.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert workspace.name == "a cool new name"


def test_view_edit_project(client, user_session):
    workspace = WorkspaceFactory.create()
    project = Projects.create(
        workspace.owner,
        workspace,
        "Snazzy Project",
        "A new project for me and my friends",
        {"env1", "env2"},
    )
    user_session(workspace.owner)
    response = client.get(
        "/workspaces/{}/projects/{}/edit".format(workspace.id, project.id)
    )
    assert response.status_code == 200


def test_user_with_permission_can_update_project(client, user_session):
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(
        owner=owner,
        projects=[
            {
                "name": "Awesome Project",
                "description": "It's really awesome!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    project = workspace.projects[0]
    user_session(owner)
    response = client.post(
        url_for(
            "workspaces.update_project",
            workspace_id=workspace.id,
            project_id=project.id,
        ),
        data={"name": "Really Cool Project", "description": "A very cool project."},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert project.name == "Really Cool Project"
    assert project.description == "A very cool project."


def test_user_without_permission_cannot_update_project(client, user_session):
    dev = UserFactory.create()
    owner = UserFactory.create()
    workspace = WorkspaceFactory.create(
        owner=owner,
        members=[{"user": dev, "role_name": "developer"}],
        projects=[
            {
                "name": "Great Project",
                "description": "Cool stuff happening here!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    project = workspace.projects[0]
    user_session(dev)
    response = client.post(
        url_for(
            "workspaces.update_project",
            workspace_id=workspace.id,
            project_id=project.id,
        ),
        data={"name": "New Name", "description": "A new description."},
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert project.name == "Great Project"
    assert project.description == "Cool stuff happening here!"


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


def test_permissions_for_view_member(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    Workspaces._create_workspace_role(user, workspace, "developer")
    member = WorkspaceUsers.add(user, workspace.id, "developer")
    user_session(user)
    response = client.post(
        url_for("workspaces.view_member", workspace_id=workspace.id, member_id=user.id),
        follow_redirects=True,
    )
    assert response.status_code == 404


def test_update_member_workspace_role(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={"workspace_role": "security_auditor"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert member.role == "security_auditor"


def test_update_member_workspace_role_with_no_data(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.update_member", workspace_id=workspace.id, member_id=user.id
        ),
        data={},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert member.role == "developer"


def test_update_member_environment_role(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
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
    assert EnvironmentRoles.get(user.id, env1_id).role == "security_auditor"
    assert EnvironmentRoles.get(user.id, env2_id).role == "devops"


def test_update_member_environment_role_with_no_data(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    member = WorkspaceUsers.add(user, workspace.id, "developer")
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
    assert EnvironmentRoles.get(user.id, env1_id).role == "developer"


def test_existing_member_accepts_valid_invite(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(user_id=user.id, workspace_role_id=ws_role.id)

    # the user does not have access to the workspace before accepting the invite
    assert len(Workspaces.for_user(user)) == 0

    user_session(user)
    response = client.get(url_for("workspaces.accept_invitation", token=invite.token))

    # user is redirected to the workspace view
    assert response.status_code == 302
    assert (
        url_for("workspaces.show_workspace", workspace_id=invite.workspace.id)
        in response.headers["Location"]
    )
    # the one-time use invite is no longer usable
    assert invite.is_accepted
    # the user has access to the workspace
    assert len(Workspaces.for_user(user)) == 1


def test_new_member_accepts_valid_invite(client, user_session):
    workspace = WorkspaceFactory.create()
    user_info = UserFactory.dictionary()

    user_session(workspace.owner)
    client.post(
        url_for("workspaces.create_member", workspace_id=workspace.id),
        data={"workspace_role": "developer", **user_info},
    )

    user = Users.get_by_dod_id(user_info["dod_id"])
    token = user.invitations[0].token

    user_session(user)
    response = client.get(url_for("workspaces.accept_invitation", token=token))

    # user is redirected to the workspace view
    assert response.status_code == 302
    assert (
        url_for("workspaces.show_workspace", workspace_id=workspace.id)
        in response.headers["Location"]
    )
    # the user has access to the workspace
    assert len(Workspaces.for_user(user)) == 1


def test_member_accepts_invalid_invite(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        user_id=user.id, workspace_role_id=ws_role.id, status=InvitationStatus.REJECTED
    )
    user_session(user)
    response = client.get(url_for("workspaces.accept_invitation", token=invite.token))

    assert response.status_code == 404


def test_user_who_has_not_accepted_workspace_invite_cannot_view(client, user_session):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()

    # create user in workspace with invitation
    user_session(workspace.owner)
    response = client.post(
        url_for("workspaces.create_member", workspace_id=workspace.id),
        data={"workspace_role": "developer", **user.to_dictionary()},
    )

    # user tries to view workspace before accepting invitation
    user_session(user)
    response = client.get("/workspaces/{}/projects".format(workspace.id))
    assert response.status_code == 404


def test_user_accepts_invite_with_wrong_dod_id(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    different_user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(user_id=user.id, workspace_role_id=ws_role.id)
    user_session(different_user)
    response = client.get(url_for("workspaces.accept_invitation", token=invite.token))

    assert response.status_code == 404


def test_user_accepts_expired_invite(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        user_id=user.id,
        workspace_role_id=ws_role.id,
        status=InvitationStatus.REJECTED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(user)
    response = client.get(url_for("workspaces.accept_invitation", token=invite.token))

    assert response.status_code == 404
