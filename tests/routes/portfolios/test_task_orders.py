from flask import url_for
import pytest

from atst.domain.roles import Roles
from atst.models.portfolio_role import Status as PortfolioStatus

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
    random_future_date,
    random_past_date,
)
from tests.utils import captured_templates


class TestPortfolioFunding:
    def test_unfunded_portfolio(self, app, user_session):
        portfolio = PortfolioFactory.create()
        user_session(portfolio.owner)

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is None
            assert context["total_balance"] == 0
            assert context["pending_task_orders"] == []
            assert context["active_task_orders"] == []
            assert context["expired_task_orders"] == []

    def test_funded_portfolio(self, app, user_session):
        portfolio = PortfolioFactory.create()
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
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is end_date
            assert context["total_balance"] == active_to1.budget + active_to2.budget


def test_ko_can_view_task_order(client, user_session):
    portfolio = PortfolioFactory.create()
    ko = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    user_session(ko)
    response = client.get(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200
