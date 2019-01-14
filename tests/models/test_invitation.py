import pytest
import datetime

from atst.models.invitation import Invitation, Status
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.factories import (
    InvitationFactory,
    PortfolioFactory,
    UserFactory,
    PortfolioRoleFactory,
)


def test_expired_invite_is_not_revokable():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = InvitationFactory.create(
        expiration_time=datetime.datetime.now() - datetime.timedelta(minutes=60),
        portfolio_role=ws_role,
    )
    assert not invite.is_revokable


def test_unexpired_invite_is_revokable():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = InvitationFactory.create(portfolio_role=ws_role)
    assert invite.is_revokable


def test_invite_is_not_revokable_if_invite_is_not_pending():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = InvitationFactory.create(portfolio_role=ws_role, status=Status.ACCEPTED)
    assert not invite.is_revokable
