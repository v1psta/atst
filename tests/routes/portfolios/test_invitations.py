import pytest
import datetime
from flask import url_for

from tests.factories import (
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    PortfolioInvitationFactory,
    TaskOrderFactory,
)
from atst.domain.portfolios import Portfolios
from atst.models import InvitationStatus, PortfolioRoleStatus
from atst.domain.users import Users
from atst.domain.permission_sets import PermissionSets


def test_existing_member_accepts_valid_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(user_id=user.id, role=ws_role)

    # the user does not have access to the portfolio before accepting the invite
    assert len(Portfolios.for_user(user)) == 0

    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    # user is redirected to the portfolio view
    assert response.status_code == 302
    assert (
        url_for("applications.portfolio_applications", portfolio_id=invite.portfolio.id)
        in response.headers["Location"]
    )
    # the one-time use invite is no longer usable
    assert invite.is_accepted
    # the user has access to the portfolio
    assert len(Portfolios.for_user(user)) == 1


def test_new_member_accepts_valid_invite(monkeypatch, client, user_session):
    portfolio = PortfolioFactory.create()
    user_info = UserFactory.dictionary()

    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.create_member", portfolio_id=portfolio.id),
        data={
            "permission_sets-perms_app_mgmt": PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
            "permission_sets-perms_funding": PermissionSets.VIEW_PORTFOLIO_FUNDING,
            "permission_sets-perms_reporting": PermissionSets.VIEW_PORTFOLIO_REPORTS,
            "permission_sets-perms_portfolio_mgmt": PermissionSets.VIEW_PORTFOLIO_ADMIN,
            "user_data-first_name": user_info["first_name"],
            "user_data-last_name": user_info["last_name"],
            "user_data-dod_id": user_info["dod_id"],
            "user_data-email": user_info["email"],
        },
    )

    assert response.status_code == 302
    user = Users.get_by_dod_id(user_info["dod_id"])
    token = user.portfolio_invitations[0].token

    monkeypatch.setattr(
        "atst.domain.auth.should_redirect_to_user_profile", lambda *args: False
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=token)
    )

    # user is redirected to the portfolio view
    assert response.status_code == 302
    assert (
        url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
        in response.headers["Location"]
    )
    # the user has access to the portfolio
    assert len(Portfolios.for_user(user)) == 1


def test_member_accepts_invalid_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id, role=ws_role, status=InvitationStatus.REJECTED_WRONG_USER
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_user_who_has_not_accepted_portfolio_invite_cannot_view(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()

    # create user in portfolio with invitation
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.create_member", portfolio_id=portfolio.id),
        data=user.to_dictionary(),
    )

    # user tries to view portfolio before accepting invitation
    user_session(user)
    response = client.get("/portfolios/{}/applications".format(portfolio.id))
    assert response.status_code == 404


def test_user_accepts_invite_with_wrong_dod_id(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    different_user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(user_id=user.id, role=ws_role)
    user_session(different_user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_user_accepts_expired_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=ws_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.accept_invitation", portfolio_token=invite.token)
    )

    assert response.status_code == 404


def test_revoke_invitation(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=ws_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 302
    assert invite.is_revoked


def test_user_can_only_revoke_invites_in_their_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        user=user, portfolio=other_portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=portfolio_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 404
    assert not invite.is_revoked


def test_user_can_only_resend_invites_in_their_portfolio(client, user_session, queue):
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    portfolio_role = PortfolioRoleFactory.create(
        user=user, portfolio=other_portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=portfolio_role,
        status=InvitationStatus.REJECTED_EXPIRED,
        expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1),
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.resend_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert response.status_code == 404
    assert len(queue.get_queue()) == 0


def test_resend_invitation_sends_email(client, user_session, queue):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id, role=ws_role, status=InvitationStatus.PENDING
    )
    user_session(portfolio.owner)
    client.post(
        url_for(
            "portfolios.resend_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    assert len(queue.get_queue()) == 1


def test_existing_member_invite_resent_to_email_submitted_in_form(
    client, user_session, queue
):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    ws_role = PortfolioRoleFactory.create(
        user=user, portfolio=portfolio, status=PortfolioRoleStatus.PENDING
    )
    invite = PortfolioInvitationFactory.create(
        user_id=user.id,
        role=ws_role,
        status=InvitationStatus.PENDING,
        email="example@example.com",
    )
    user_session(portfolio.owner)
    client.post(
        url_for(
            "portfolios.resend_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
    )

    send_mail_job = queue.get_queue().jobs[0]
    assert user.email != "example@example.com"
    assert send_mail_job.func.__func__.__name__ == "_send_mail"
    assert send_mail_job.args[0] == ["example@example.com"]
