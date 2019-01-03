from tests.factories import UserFactory, WorkspaceFactory

from atst.services.invitation import Invitation


def test_invite_member(queue):
    inviter = UserFactory.create()
    new_member = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=inviter)
    invite_service = Invitation(
        inviter,
        workspace,
        {**new_member.to_dictionary(), "workspace_role": "developer"},
    )
    new_invitation = invite_service.invite()
    assert new_invitation == new_member.invitations[0]
    assert len(queue.get_queue()) == 1
