import datetime
from flask import url_for

from tests.factories import (
    UserFactory,
    WorkspaceFactory,
    WorkspaceRoleFactory,
    InvitationFactory,
)
from atst.domain.workspaces import Workspaces
from atst.models.workspace_role import Status as WorkspaceRoleStatus
from atst.models.invitation import Status as InvitationStatus
from atst.domain.users import Users


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


def test_new_member_accepts_valid_invite(monkeypatch, client, user_session):
    workspace = WorkspaceFactory.create()
    user_info = UserFactory.dictionary()

    user_session(workspace.owner)
    client.post(
        url_for("workspaces.create_member", workspace_id=workspace.id),
        data={"workspace_role": "developer", **user_info},
    )

    user = Users.get_by_dod_id(user_info["dod_id"])
    token = user.invitations[0].token

    monkeypatch.setattr(
        "atst.domain.auth.should_redirect_to_user_profile", lambda *args: False
    )
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
        user_id=user.id,
        workspace_role_id=ws_role.id,
        status=InvitationStatus.REJECTED_WRONG_USER,
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
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(user)
    response = client.get(url_for("workspaces.accept_invitation", token=invite.token))

    assert response.status_code == 404


def test_revoke_invitation(client, user_session):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        user_id=user.id,
        workspace_role_id=ws_role.id,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(workspace.owner)
    response = client.post(
        url_for(
            "workspaces.revoke_invitation",
            workspace_id=workspace.id,
            token=invite.token,
        )
    )

    assert response.status_code == 302
    assert invite.is_revoked


def test_resend_invitation_sends_email(client, user_session, queue):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        user_id=user.id, workspace_role_id=ws_role.id, status=InvitationStatus.PENDING
    )
    user_session(workspace.owner)
    client.post(
        url_for(
            "workspaces.resend_invitation",
            workspace_id=workspace.id,
            token=invite.token,
        )
    )

    assert len(queue.get_queue()) == 1


def test_existing_member_invite_resent_to_email_submitted_in_form(
    client, user_session, queue
):
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        user=user, workspace=workspace, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        user_id=user.id,
        workspace_role_id=ws_role.id,
        status=InvitationStatus.PENDING,
        email="example@example.com",
    )
    user_session(workspace.owner)
    client.post(
        url_for(
            "workspaces.resend_invitation",
            workspace_id=workspace.id,
            token=invite.token,
        )
    )

    send_mail_job = queue.get_queue().jobs[0]
    assert user.email != "example@example.com"
    assert send_mail_job.func.__func__.__name__ == "_send_mail"
    assert send_mail_job.args[0] == ["example@example.com"]
