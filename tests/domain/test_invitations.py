import datetime
import pytest
import re

from atst.domain.invitations import Invitations, InvitationError
from atst.models.invitation import Status

from tests.factories import WorkspaceFactory, UserFactory, InvitationFactory


def test_create_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = Invitations.create(workspace, workspace.owner, user)
    assert invite.user == user
    assert invite.workspace == workspace
    assert invite.inviter == workspace.owner
    assert invite.status == Status.PENDING
    assert re.match(r"^[\w\-_]+$", invite.token)


def test_accept_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = Invitations.create(workspace, workspace.owner, user)
    assert invite.is_pending
    accepted_invite = Invitations.accept(invite.token)
    assert accepted_invite.is_accepted


def test_accept_expired_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    increment = Invitations.EXPIRATION_LIMIT_MINUTES + 1
    expiration_time = datetime.datetime.now() - datetime.timedelta(minutes=increment)
    invite = InvitationFactory.create(
        workspace_id=workspace.id,
        user_id=user.id,
        expiration_time=expiration_time,
        status=Status.PENDING,
    )
    with pytest.raises(InvitationError):
        Invitations.accept(invite.token)

    assert invite.is_rejected


def test_accept_rejected_invite():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = InvitationFactory.create(
        workspace_id=workspace.id, user_id=user.id, status=Status.REJECTED
    )
    with pytest.raises(InvitationError):
        Invitations.accept(invite.token)


def test_accept_revoked_invite():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = InvitationFactory.create(
        workspace_id=workspace.id, user_id=user.id, status=Status.REVOKED
    )
    with pytest.raises(InvitationError):
        Invitations.accept(invite.token)
