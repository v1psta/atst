import datetime
import pytest
import re

from atst.domain.invitations import (
    PortfolioInvitations,
    InvitationError,
    WrongUserError,
    ExpiredError,
    NotFoundError,
)
from atst.domain.audit_log import AuditLog
from atst.models import InvitationStatus

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    UserFactory,
    PortfolioInvitationFactory,
)


def test_create_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    assert invite.user == user
    assert invite.role == ws_role
    assert invite.inviter == portfolio.owner
    assert invite.status == InvitationStatus.PENDING
    assert re.match(r"^[\w\-_]+$", invite.token)


def test_accept_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    assert invite.is_pending
    accepted_invite = PortfolioInvitations.accept(user, invite.token)
    assert accepted_invite.is_accepted


def test_accept_expired_invitation():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    increment = PortfolioInvitations.EXPIRATION_LIMIT_MINUTES + 1
    expiration_time = datetime.datetime.now() - datetime.timedelta(minutes=increment)
    invite = PortfolioInvitationFactory.create(
        user=user,
        expiration_time=expiration_time,
        status=InvitationStatus.PENDING,
        role=ws_role,
    )
    with pytest.raises(ExpiredError):
        PortfolioInvitations.accept(user, invite.token)

    assert invite.is_rejected


def test_accept_rejected_invite():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(
        user=user, status=InvitationStatus.REJECTED_EXPIRED, role=ws_role
    )
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)


def test_accept_revoked_invite():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(
        user=user, status=InvitationStatus.REVOKED, role=ws_role
    )
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)


def test_wrong_user_accepts_invitation():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    wrong_user = UserFactory.create()
    invite = PortfolioInvitationFactory.create(user=user, role=ws_role)
    with pytest.raises(WrongUserError):
        PortfolioInvitations.accept(wrong_user, invite.token)


def test_user_cannot_accept_invitation_accepted_by_wrong_user():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    wrong_user = UserFactory.create()
    invite = PortfolioInvitationFactory.create(user=user, role=ws_role)
    with pytest.raises(WrongUserError):
        PortfolioInvitations.accept(wrong_user, invite.token)
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)


def test_accept_invitation_twice():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    PortfolioInvitations.accept(user, invite.token)
    with pytest.raises(InvitationError):
        PortfolioInvitations.accept(user, invite.token)


def test_revoke_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    assert invite.is_pending
    PortfolioInvitations.revoke(invite.token)
    assert invite.is_revoked


def test_resend_invitation():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    PortfolioInvitations.resend(user, invite.token)
    assert ws_role.invitations[0].is_revoked
    assert ws_role.invitations[1].is_pending


def test_audit_event_for_accepted_invite():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)
    invite = PortfolioInvitations.accept(user, invite.token)

    accepted_event = AuditLog.get_by_resource(invite.id)[0]
    assert "email" in accepted_event.event_details
    assert "dod_id" in accepted_event.event_details


def test_lookup_by_user_and_portfolio():
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(user=user, portfolio=portfolio)
    invite = PortfolioInvitations.create(portfolio.owner, ws_role, user.email)

    assert PortfolioInvitations.lookup_by_resource_and_user(portfolio, user) == invite

    with pytest.raises(NotFoundError):
        PortfolioInvitations.lookup_by_resource_and_user(
            portfolio, UserFactory.create()
        )
