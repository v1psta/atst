import pytest
import datetime

from atst.models.invitation import Invitation, Status

from tests.factories import InvitationFactory


def test_expired_invite_is_not_revokable():
    invite = InvitationFactory.create(
        expiration_time=datetime.datetime.now() - datetime.timedelta(minutes=60)
    )
    assert not invite.is_revokable


def test_unexpired_invite_is_revokable():
    invite = InvitationFactory.create()
    assert invite.is_revokable


def test_invite_is_not_revokable_if_invite_is_not_pending():
    invite = InvitationFactory.create(status=Status.ACCEPTED)
    assert not invite.is_revokable
