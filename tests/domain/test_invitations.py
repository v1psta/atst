import datetime
import pytest
import re

from atst.domain.invitations import (
    Invitations,
    InvitationError,
    WrongUserError,
    ExpiredError,
)
from atst.models.invitation import Status

from tests.factories import (
    WorkspaceFactory,
    WorkspaceRoleFactory,
    UserFactory,
    InvitationFactory,
)

from atst.domain.audit_log import AuditLog


def test_create_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    assert invite.user == user
    assert invite.workspace_role == ws_role
    assert invite.inviter == workspace.owner
    assert invite.status == Status.PENDING
    assert re.match(r"^[\w\-_]+$", invite.token)


def test_accept_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    assert invite.is_pending
    accepted_invite = Invitations.accept(user, invite.token)
    assert accepted_invite.is_accepted


def test_accept_expired_invitation():
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    increment = Invitations.EXPIRATION_LIMIT_MINUTES + 1
    expiration_time = datetime.datetime.now() - datetime.timedelta(minutes=increment)
    invite = InvitationFactory.create(
        user=user,
        expiration_time=expiration_time,
        status=Status.PENDING,
        workspace_role=ws_role,
    )
    with pytest.raises(ExpiredError):
        Invitations.accept(user, invite.token)

    assert invite.is_rejected


def test_accept_rejected_invite():
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = InvitationFactory.create(
        user=user, status=Status.REJECTED_EXPIRED, workspace_role=ws_role
    )
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_accept_revoked_invite():
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = InvitationFactory.create(
        user=user, status=Status.REVOKED, workspace_role=ws_role
    )
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_wrong_user_accepts_invitation():
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    wrong_user = UserFactory.create()
    invite = InvitationFactory.create(user=user, workspace_role=ws_role)
    with pytest.raises(WrongUserError):
        Invitations.accept(wrong_user, invite.token)


def test_user_cannot_accept_invitation_accepted_by_wrong_user():
    user = UserFactory.create()
    workspace = WorkspaceFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    wrong_user = UserFactory.create()
    invite = InvitationFactory.create(user=user, workspace_role=ws_role)
    with pytest.raises(WrongUserError):
        Invitations.accept(wrong_user, invite.token)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_accept_invitation_twice():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    Invitations.accept(user, invite.token)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_revoke_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    assert invite.is_pending
    Invitations.revoke(invite.token)
    assert invite.is_revoked


def test_resend_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    Invitations.resend(workspace.owner, workspace.id, invite.token)
    assert ws_role.invitations[0].is_revoked
    assert ws_role.invitations[1].is_pending


def test_audit_event_for_accepted_invite():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role, user.email)
    invite = Invitations.accept(user, invite.token)

    accepted_event = AuditLog.get_by_resource(invite.id)[0]
    assert "email" in accepted_event.event_details
    assert "dod_id" in accepted_event.event_details
