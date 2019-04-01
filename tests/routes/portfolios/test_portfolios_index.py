from flask import url_for

from atst.domain.permission_sets import PermissionSets
from atst.models.permissions import Permissions
from atst.domain.portfolio_roles import PortfolioRoles
from atst.models.portfolio_role import Status as PortfolioRoleStatus

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


def test_remove_portfolio_member(client, user_session):
    portfolio = PortfolioFactory.create()

    user = UserFactory.create()
    PortfolioRoleFactory.create(portfolio=portfolio, user=user)

    user_session(portfolio.owner)

    response = client.post(
        url_for(
            "portfolios.remove_member", portfolio_id=portfolio.id, member_id=user.id
        ),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "portfolios.portfolio_admin",
        portfolio_id=portfolio.id,
        _anchor="portfolio-members",
        fragment="portfolio-members",
        _external=True,
    )
    assert (
        PortfolioRoles.get(portfolio_id=portfolio.id, user_id=user.id).status
        == PortfolioRoleStatus.DISABLED
    )


def test_remove_portfolio_member_self(client, user_session):
    portfolio = PortfolioFactory.create()

    user_session(portfolio.owner)

    response = client.post(
        url_for(
            "portfolios.remove_member",
            portfolio_id=portfolio.id,
            member_id=portfolio.owner.id,
        ),
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert (
        PortfolioRoles.get(portfolio_id=portfolio.id, user_id=portfolio.owner.id).status
        == PortfolioRoleStatus.ACTIVE
    )


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
