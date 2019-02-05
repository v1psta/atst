from flask import url_for
import pytest

from atst.domain.roles import Roles
from atst.domain.task_orders import TaskOrders
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


class TestTaskOrderInvitations:
    def setup(self):
        self.portfolio = PortfolioFactory.create()
        self.task_order = TaskOrderFactory.create(portfolio=self.portfolio)

    def _post(self, client, updates):
        return client.post(
            url_for(
                "portfolios.edit_task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=self.task_order.id,
            ),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=updates,
        )

    def test_editing_with_partial_data(self, user_session, client):
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-first_name": "Luke",
                "contracting_officer-last_name": "Skywalker",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )
        updated_task_order = TaskOrders.get(self.portfolio.owner, self.task_order.id)
        assert updated_task_order.ko_first_name == "Luke"
        assert updated_task_order.ko_last_name == "Skywalker"
        assert updated_task_order.so_first_name == "Boba"
        assert updated_task_order.so_last_name == "Fett"

    def test_editing_with_invalid_data(self, user_session, client):
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-phone_number": "invalid input",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )

        assert "There were some errors" in response.data.decode()

        updated_task_order = TaskOrders.get(self.portfolio.owner, self.task_order.id)
        assert updated_task_order.so_first_name != "Boba"


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


def test_can_view_task_order_invitations(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    response = client.get(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200


def test_ko_can_view_ko_review_page(client, user_session):
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
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200


def test_mo_redirected_to_build_page(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_cor_redirected_to_build_page(client, user_session):
    portfolio = PortfolioFactory.create()
    cor = UserFactory.create()
    PortfolioRoleFactory.create(
        role=Roles.get("officer"),
        portfolio=portfolio,
        user=cor,
        status=PortfolioStatus.ACTIVE,
    )
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer_representative=cor
    )
    user_session(cor)
    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200
