from tests.factories import UserFactory, WorkspaceFactory, WorkspaceRoleFactory

from atst.services.invitation import Invitation


def test_invite_member(queue):
    inviter = UserFactory.create()
    new_member = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=inviter)
    ws_member = WorkspaceRoleFactory.create(user=new_member, workspace=workspace)
    invite_service = Invitation(inviter, ws_member, new_member.email)
    new_invitation = invite_service.invite()
    assert new_invitation == new_member.invitations[0]
    assert len(queue.get_queue()) == 1
