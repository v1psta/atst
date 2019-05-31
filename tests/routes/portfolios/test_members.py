from flask import url_for

from atst.domain.permission_sets import PermissionSets
from atst.models import PortfolioInvitation
from atst.queue import queue

from tests.factories import UserFactory, PortfolioFactory

_DEFAULT_PERMS_FORM_DATA = {
    "permission_sets-perms_app_mgmt": PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
    "permission_sets-perms_funding": PermissionSets.VIEW_PORTFOLIO_FUNDING,
    "permission_sets-perms_reporting": PermissionSets.VIEW_PORTFOLIO_REPORTS,
    "permission_sets-perms_portfolio_mgmt": PermissionSets.VIEW_PORTFOLIO_ADMIN,
}


def test_user_with_permission_has_add_member_link(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(url_for("portfolios.admin", portfolio_id=portfolio.id))
    assert response.status_code == 200
    assert (
        url_for("portfolios.create_member", portfolio_id=portfolio.id).encode()
        in response.data
    )


def test_create_member(client, user_session, session):
    user_data = UserFactory.dictionary()
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    queue_length = len(queue.get_queue())

    response = client.post(
        url_for("portfolios.create_member", portfolio_id=portfolio.id),
        data={
            "user_data-dod_id": user_data.get("dod_id"),
            "user_data-first_name": user_data.get("first_name"),
            "user_data-last_name": user_data.get("last_name"),
            "user_data-email": user_data.get("email"),
            **_DEFAULT_PERMS_FORM_DATA,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    full_name = "{} {}".format(user_data.get("first_name"), user_data.get("last_name"))
    assert full_name in response.data.decode()

    invitation = (
        session.query(PortfolioInvitation)
        .filter_by(dod_id=user_data.get("dod_id"))
        .one()
    )
    assert invitation.role.portfolio == portfolio

    assert len(queue.get_queue()) == queue_length + 1
    assert len(invitation.role.permission_sets) == 5
