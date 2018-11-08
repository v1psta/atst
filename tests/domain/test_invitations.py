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


def test_create_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role)
    assert invite.user == user
    assert invite.workspace_role == ws_role
    assert invite.inviter == workspace.owner
    assert invite.status == Status.PENDING
    assert re.match(r"^[\w\-_]+$", invite.token)


def test_accept_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role)
    assert invite.is_pending
    accepted_invite = Invitations.accept(user, invite.token)
    assert accepted_invite.is_accepted


def test_accept_expired_invitation():
    user = UserFactory.create()
    increment = Invitations.EXPIRATION_LIMIT_MINUTES + 1
    expiration_time = datetime.datetime.now() - datetime.timedelta(minutes=increment)
    invite = InvitationFactory.create(
        user_id=user.id, expiration_time=expiration_time, status=Status.PENDING
    )
    with pytest.raises(ExpiredError):
        Invitations.accept(user, invite.token)

    assert invite.is_rejected


def test_accept_rejected_invite():
    user = UserFactory.create()
    invite = InvitationFactory.create(user_id=user.id, status=Status.REJECTED_EXPIRED)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_accept_revoked_invite():
    user = UserFactory.create()
    invite = InvitationFactory.create(user_id=user.id, status=Status.REVOKED)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_wrong_user_accepts_invitation():
    user = UserFactory.create()
    wrong_user = UserFactory.create()
    invite = InvitationFactory.create(user_id=user.id)
    with pytest.raises(WrongUserError):
        Invitations.accept(wrong_user, invite.token)


def test_user_cannot_accept_invitation_accepted_by_wrong_user():
    user = UserFactory.create()
    wrong_user = UserFactory.create()
    invite = InvitationFactory.create(user_id=user.id)
    with pytest.raises(WrongUserError):
        Invitations.accept(wrong_user, invite.token)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_accept_invitation_twice():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role)
    Invitations.accept(user, invite.token)
    with pytest.raises(InvitationError):
        Invitations.accept(user, invite.token)


def test_revoke_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(user=user, workspace=workspace)
    invite = Invitations.create(workspace.owner, ws_role)
    assert invite.is_pending
    Invitations.revoke(invite.token)
    assert invite.is_revoked
