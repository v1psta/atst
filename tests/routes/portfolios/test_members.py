from flask import url_for

from tests.factories import (
    UserFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    InvitationFactory,
)
from atst.domain.portfolios import Portfolios
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.applications import Applications
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.queue import queue
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from atst.models.invitation import Status as InvitationStatus


def create_portfolio_and_invite_user(
    ws_role="developer",
    ws_status=PortfolioRoleStatus.PENDING,
    invite_status=InvitationStatus.PENDING,
):
    portfolio = PortfolioFactory.create()
    if ws_role != "owner":
        user = UserFactory.create()
        member = PortfolioRoleFactory.create(
            user=user, portfolio=portfolio, status=ws_status
        )
        InvitationFactory.create(
            user=portfolio.owner,
            portfolio_role=member,
            email=member.user.email,
            status=invite_status,
        )
    return portfolio


def test_user_with_permission_has_add_member_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get("/portfolios/{}/members".format(portfolio.id))
    assert (
        'href="/portfolios/{}/members/new"'.format(portfolio.id).encode()
        in response.data
    )


def test_user_without_permission_has_no_add_member_link(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio, "developer")
    user_session(user)
    response = client.get("/portfolios/{}/members".format(portfolio.id))
    assert (
        'href="/portfolios/{}/members/new"'.format(portfolio.id).encode()
        not in response.data
    )


def test_permissions_for_view_member(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio, "developer")
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    user_session(user)
    response = client.get(
        url_for("portfolios.view_member", portfolio_id=portfolio.id, member_id=user.id)
    )
    assert response.status_code == 404


def test_create_member(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    queue_length = len(queue.get_queue())

    response = client.post(
        url_for("portfolios.create_member", portfolio_id=portfolio.id),
        data={
            "dod_id": user.dod_id,
            "first_name": "Wilbur",
            "last_name": "Zuckerman",
            "email": "some_pig@zuckermans.com",
            "portfolio_role": "developer",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert user.has_portfolios
    assert user.invitations
    assert len(queue.get_queue()) == queue_length + 1


def test_view_member_shows_role(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    Portfolios._create_portfolio_role(user, portfolio, "developer")
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    user_session(portfolio.owner)
    response = client.get(
        url_for("portfolios.view_member", portfolio_id=portfolio.id, member_id=user.id)
    )
    assert response.status_code == 200
    assert "initial-choice='developer'".encode() in response.data


def test_update_member_portfolio_role(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.update_member", portfolio_id=portfolio.id, member_id=user.id
        ),
        data={"portfolio_role": "security_auditor"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"role updated successfully" in response.data
    assert member.role_name == "security_auditor"


def test_update_member_portfolio_role_with_no_data(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.update_member", portfolio_id=portfolio.id, member_id=user.id
        ),
        data={},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert member.role_name == "developer"


def test_update_member_environment_role(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    env1_id = application.environments[0].id
    env2_id = application.environments[1].id
    for env in application.environments:
        Environments.add_member(env, user, "developer")
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.update_member", portfolio_id=portfolio.id, member_id=user.id
        ),
        data={
            "portfolio_role": "developer",
            "env_" + str(env1_id): "security_auditor",
            "env_" + str(env2_id): "devops",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"role updated successfully" not in response.data
    assert b"access successfully changed" in response.data
    assert EnvironmentRoles.get(user.id, env1_id).role == "security_auditor"
    assert EnvironmentRoles.get(user.id, env2_id).role == "devops"


def test_update_member_environment_role_with_no_data(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    member = PortfolioRoles.add(user, portfolio.id, "developer")
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1"},
    )
    env1_id = application.environments[0].id
    for env in application.environments:
        Environments.add_member(env, user, "developer")
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.update_member", portfolio_id=portfolio.id, member_id=user.id
        ),
        data={"env_" + str(env1_id): None, "env_" + str(env1_id): ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"access successfully changed" not in response.data
    assert EnvironmentRoles.get(user.id, env1_id).role == "developer"


def test_revoke_active_member_access(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    member = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioRoleStatus.ACTIVE
    )
    Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1"},
    )
    user_session(portfolio.owner)
    response = client.post(
        url_for(
            "portfolios.revoke_access", portfolio_id=portfolio.id, member_id=member.id
        )
    )
    assert response.status_code == 302
    assert PortfolioRoles.get_by_id(member.id).num_environment_roles == 0


def test_does_not_show_any_buttons_if_owner(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for(
            "portfolios.view_member",
            portfolio_id=portfolio.id,
            member_id=portfolio.owner.id,
        )
    )
    assert "Remove Portfolio Access" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()


def test_only_shows_revoke_access_button_if_active(client, user_session):
    portfolio = create_portfolio_and_invite_user(
        ws_status=PortfolioRoleStatus.ACTIVE, invite_status=InvitationStatus.ACCEPTED
    )
    user_session(portfolio.owner)
    member = portfolio.members[1]
    response = client.get(
        url_for(
            "portfolios.view_member",
            portfolio_id=portfolio.id,
            member_id=member.user.id,
        )
    )
    assert "Remove Portfolio Access" in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()


def test_only_shows_revoke_invite_button_if_pending(client, user_session):
    portfolio = create_portfolio_and_invite_user(
        ws_status=PortfolioRoleStatus.PENDING, invite_status=InvitationStatus.PENDING
    )
    user_session(portfolio.owner)
    member = portfolio.members[1]
    response = client.get(
        url_for(
            "portfolios.view_member",
            portfolio_id=portfolio.id,
            member_id=member.user.id,
        )
    )
    assert "Revoke Invitation" in response.data.decode()
    assert "Remove Portfolio Access" not in response.data.decode()
    assert "Resend Invitation" not in response.data.decode()


def test_only_shows_resend_button_if_expired(client, user_session):
    portfolio = create_portfolio_and_invite_user(
        ws_status=PortfolioRoleStatus.PENDING,
        invite_status=InvitationStatus.REJECTED_EXPIRED,
    )
    user_session(portfolio.owner)
    member = portfolio.members[1]
    response = client.get(
        url_for(
            "portfolios.view_member",
            portfolio_id=portfolio.id,
            member_id=member.user.id,
        )
    )
    assert "Resend Invitation" in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
    assert "Remove Portfolio Access" not in response.data.decode()


def test_only_shows_resend_button_if_revoked(client, user_session):
    portfolio = create_portfolio_and_invite_user(
        ws_status=PortfolioRoleStatus.PENDING, invite_status=InvitationStatus.REVOKED
    )
    user_session(portfolio.owner)
    member = portfolio.members[1]
    response = client.get(
        url_for(
            "portfolios.view_member",
            portfolio_id=portfolio.id,
            member_id=member.user.id,
        )
    )
    assert "Resend Invitation" in response.data.decode()
    assert "Remove Portfolio Access" not in response.data.decode()
    assert "Revoke Invitation" not in response.data.decode()
