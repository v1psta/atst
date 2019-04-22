from flask import url_for

from tests.factories import UserFactory, PortfolioFactory
from atst.domain.permission_sets import PermissionSets
from atst.queue import queue

_DEFAULT_PERMS_FORM_DATA = {
    "perms_app_mgmt": PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
    "perms_funding": PermissionSets.VIEW_PORTFOLIO_FUNDING,
    "perms_reporting": PermissionSets.VIEW_PORTFOLIO_REPORTS,
    "perms_portfolio_mgmt": PermissionSets.VIEW_PORTFOLIO_ADMIN,
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
            **_DEFAULT_PERMS_FORM_DATA,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert user.full_name in response.data.decode()
    assert user.has_portfolios
    assert user.portfolio_invitations
    assert len(queue.get_queue()) == queue_length + 1
    portfolio_role = user.portfolio_roles[0]
    assert len(portfolio_role.permission_sets) == 5
