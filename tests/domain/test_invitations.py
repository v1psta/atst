import datetime
import pytest

from atst.domain.invitations import Invitations, InvitationExpired

from tests.factories import WorkspaceFactory, UserFactory, InvitationFactory


def test_create_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = Invitations.create(workspace, user)
    assert invite.user == user
    assert invite.workspace == workspace
    assert invite.valid


def test_accept_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = Invitations.create(workspace, user)
    assert invite.valid
    accepted_invite = Invitations.accept(invite.id)
    assert not accepted_invite.valid


def test_accept_expired_invitation():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    increment = Invitations.EXPIRATION_LIMIT_MINUTES + 1
    created_at = datetime.datetime.now() - datetime.timedelta(minutes=increment)
    invite = InvitationFactory.create(
        workspace_id=workspace.id, user_id=user.id, time_created=created_at, valid=True
    )
    with pytest.raises(InvitationExpired):
        Invitations.accept(invite.id)

    assert not invite.valid


def test_accept_invalid_invite():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    invite = InvitationFactory.create(
        workspace_id=workspace.id, user_id=user.id, valid=False
    )
    with pytest.raises(InvitationExpired):
        Invitations.accept(invite.id)
