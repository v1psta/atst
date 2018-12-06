import pytest
import datetime

from atst.models.invitation import Invitation, Status
from atst.models.workspace_role import Status as WorkspaceRoleStatus

from tests.factories import (
    InvitationFactory,
    WorkspaceFactory,
    UserFactory,
    WorkspaceRoleFactory,
)


def test_expired_invite_is_not_revokable():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        expiration_time=datetime.datetime.now() - datetime.timedelta(minutes=60),
        workspace_role=ws_role,
    )
    assert not invite.is_revokable


def test_unexpired_invite_is_revokable():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(workspace_role=ws_role)
    assert invite.is_revokable


def test_invite_is_not_revokable_if_invite_is_not_pending():
    workspace = WorkspaceFactory.create()
    user = UserFactory.create()
    ws_role = WorkspaceRoleFactory.create(
        workspace=workspace, user=user, status=WorkspaceRoleStatus.PENDING
    )
    invite = InvitationFactory.create(workspace_role=ws_role, status=Status.ACCEPTED)
    assert not invite.is_revokable
