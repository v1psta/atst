import pytest

from flask import url_for
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolios import Portfolios
from atst.models.permissions import Permissions
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.exceptions import UnauthorizedError

from tests.factories import (
    random_future_date,
    random_past_date,
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
)
from atst.utils.localization import translate


def test_update_portfolio_name(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.post(
        url_for("portfolios.edit_portfolio", portfolio_id=portfolio.id),
        data={"name": "a cool new name"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert portfolio.name == "a cool new name"


def updating_ppoc_successfully(client, old_ppoc, new_ppoc, portfolio):
    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"user_id": new_ppoc.id},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "portfolios.portfolio_applications", portfolio_id=portfolio.id, _external=True
    )
    assert portfolio.owner.id == new_ppoc.id
    assert (
        Permissions.EDIT_PORTFOLIO_POC
        in PortfolioRoles.get(
            portfolio_id=portfolio.id, user_id=new_ppoc.id
        ).permissions
    )
    assert (
        Permissions.EDIT_PORTFOLIO_POC
        not in PortfolioRoles.get(portfolio.id, old_ppoc.id).permissions
    )

    #
    # TODO: assert ppoc change is in audit trail
    #


def test_update_ppoc_to_member_not_on_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner
    non_portfolio_member = UserFactory.create()

    user_session(original_ppoc)

    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"user_id": non_portfolio_member.id},
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert portfolio.owner.id == original_ppoc.id


def test_update_ppoc_when_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner
    new_ppoc = UserFactory.create()
    Portfolios.add_member(
        member=new_ppoc,
        portfolio=portfolio,
        permission_sets=[PermissionSets.VIEW_PORTFOLIO],
    )

    user_session(original_ppoc)

    updating_ppoc_successfully(
        client=client, new_ppoc=new_ppoc, old_ppoc=original_ppoc, portfolio=portfolio
    )


def test_update_ppoc_when_cpo(client, user_session):
    ccpo = UserFactory.create_ccpo()
    portfolio = PortfolioFactory.create()
    original_ppoc = portfolio.owner
    new_ppoc = UserFactory.create()
    Portfolios.add_member(
        member=new_ppoc,
        portfolio=portfolio,
        permission_sets=[PermissionSets.VIEW_PORTFOLIO],
    )

    user_session(ccpo)

    updating_ppoc_successfully(
        client=client, new_ppoc=new_ppoc, old_ppoc=original_ppoc, portfolio=portfolio
    )


def test_update_ppoc_when_not_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    new_owner = UserFactory.create()

    user_session(new_owner)

    response = client.post(
        url_for("portfolios.update_ppoc", portfolio_id=portfolio.id, _external=True),
        data={"dod_id": new_owner.dod_id},
        follow_redirects=False,
    )

    assert response.status_code == 404

    # No update to portfolio ppoc
    # No audit log change? Do we log invalid request?
    # No permission change for old ppoc
    # No permission change for attempted new ppoc


def test_portfolio_index_with_existing_portfolios(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)

    response = client.get(url_for("portfolios.portfolios"))

    assert response.status_code == 200
    assert portfolio.name.encode("utf8") in response.data
    assert (
        translate("portfolios.index.empty.start_button").encode("utf8")
        not in response.data
    )


def test_portfolio_index_without_existing_portfolios(client, user_session):
    user = UserFactory.create()
    user_session(user)

    response = client.get(url_for("portfolios.portfolios"))

    assert response.status_code == 200
    assert (
        translate("portfolios.index.empty.start_button").encode("utf8") in response.data
    )


def test_portfolio_admin_screen_when_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    response = client.get(
        url_for("portfolios.portfolio_admin", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()
    assert translate("fragments.ppoc.update_btn").encode("utf8") in response.data


def test_portfolio_admin_screen_when_not_ppoc(client, user_session):
    portfolio = PortfolioFactory.create()
    user = UserFactory.create()
    permission_sets = PermissionSets.get_many(
        [PermissionSets.EDIT_PORTFOLIO_ADMIN, PermissionSets.VIEW_PORTFOLIO_ADMIN]
    )
    PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, permission_sets=permission_sets
    )
    user_session(user)
    response = client.get(
        url_for("portfolios.portfolio_admin", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()
    assert translate("fragments.ppoc.update_btn").encode("utf8") not in response.data


def test_portfolio_reports(client, user_session):
    portfolio = PortfolioFactory.create(
        applications=[
            {"name": "application1", "environments": [{"name": "application1 prod"}]}
        ]
    )
    task_order = TaskOrderFactory.create(
        number="42",
        start_date=random_past_date(),
        end_date=random_future_date(),
        portfolio=portfolio,
    )
    user_session(portfolio.owner)
    response = client.get(
        url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()
    expiration_date = task_order.end_date.strftime("%Y-%m-%d")
    assert expiration_date in response.data.decode()


def test_portfolio_reports_with_mock_portfolio(client, user_session):
    portfolio = PortfolioFactory.create(name="A-Wing")
    user_session(portfolio.owner)
    response = client.get(
        url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200
    assert portfolio.name in response.data.decode()
    assert "$251,626.00 Total spend to date" in response.data.decode()
