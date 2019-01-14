from tests.factories import UserFactory, PortfolioFactory, PortfolioRoleFactory

from atst.services.invitation import Invitation


def test_invite_member(queue):
    inviter = UserFactory.create()
    new_member = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=inviter)
    ws_member = PortfolioRoleFactory.create(user=new_member, portfolio=portfolio)
    invite_service = Invitation(inviter, ws_member, new_member.email)
    new_invitation = invite_service.invite()
    assert new_invitation == new_member.invitations[0]
    assert len(queue.get_queue()) == 1
