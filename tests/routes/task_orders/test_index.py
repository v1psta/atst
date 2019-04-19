from flask import url_for
import pytest
from datetime import timedelta, date

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models.portfolio_role import Status as PortfolioStatus
from atst.utils.localization import translate

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
    random_future_date,
    random_past_date,
)
from tests.utils import captured_templates


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


class TestPortfolioFunding:
    def test_portfolio_with_no_task_orders(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is None
            assert context["total_balance"] == 0
            assert context["pending_task_orders"] == []
            assert context["active_task_orders"] == []
            assert context["expired_task_orders"] == []

    def test_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        pending_to = TaskOrderFactory.create(portfolio=portfolio)
        active_to1 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="42",
        )
        active_to2 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="43",
        )
        end_date = (
            active_to1.end_date
            if active_to1.end_date > active_to2.end_date
            else active_to2.end_date
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is end_date
            assert context["total_balance"] == active_to1.budget + active_to2.budget

    def test_expiring_and_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )
        active_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(year_min=1, year_max=2),
            number="43",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is active_to.end_date
            assert context["funded"] == True

    def test_expiring_and_unfunded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is expiring_to.end_date
            assert context["funded"] == False

    def test_user_can_only_access_to_in_their_portfolio(
        self, app, user_session, portfolio
    ):
        other_task_order = TaskOrderFactory.create()
        user_session(portfolio.owner)
        response = app.test_client().get(
            url_for("task_orders.view_task_order", task_order_id=other_task_order.id)
        )
        assert response.status_code == 404


def test_ko_can_view_task_order(client, user_session, portfolio, user):
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=user,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=user)
    user_session(user)

    response = client.get(
        url_for("task_orders.view_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 200
    assert translate("common.manage") in response.data.decode()

    TaskOrders.update(task_order, clin_01=None)
    response = client.get(
        url_for("task_orders.view_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 200
    assert translate("common.manage") not in response.data.decode()
