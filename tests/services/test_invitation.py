from tests.factories import (
    ApplicationFactory,
    ApplicationRoleFactory,
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
)

from atst.services.invitation import Invitation


def test_invite_portfolio_member(queue):
    inviter = UserFactory.create()
    new_member = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=inviter)
    ws_member = PortfolioRoleFactory.create(user=new_member, portfolio=portfolio)
    invite_service = Invitation(inviter, ws_member, new_member.email)
    new_invitation = invite_service.invite()
    assert new_invitation == new_member.portfolio_invitations[0]
    assert len(queue.get_queue()) == 1


def test_invite_application_member(queue):
    inviter = UserFactory.create()
    new_member = UserFactory.create()
    application = ApplicationFactory.create()
    member = ApplicationRoleFactory.create(user=new_member, application=application)
    invite_service = Invitation(inviter, member, new_member.email)
    new_invitation = invite_service.invite()
    assert new_invitation == new_member.application_invitations[0]
    assert len(queue.get_queue()) == 1
