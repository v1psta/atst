from flask import url_for
import pytest
from datetime import timedelta, date

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models import *
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

@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    attachment = Attachment(filename="sample_attachment", object_name="sample")

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


def test_review_task_order(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.get(url_for("task_orders.review_task_order", task_order_id=task_order.id))
    assert response.status_code == 200

def test_submit_task_order(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for(
            "task_orders.submit_task_order", task_order_id=task_order.id
        ),
    )
    assert response.status_code == 302


class TestPortfolioFunding:
    @pytest.mark.skip(reason="Update later when CLINs are implemented")
    def test_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        pending_to = TaskOrderFactory.create(portfolio=portfolio)
        active_to1 = TaskOrderFactory.create(portfolio=portfolio, number="42")
        active_to2 = TaskOrderFactory.create(portfolio=portfolio, number="43")
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

    @pytest.mark.skip(reason="Update later when CLINs are implemented")
    def test_expiring_and_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(portfolio=portfolio, number="42")
        active_to = TaskOrderFactory.create(portfolio=portfolio, number="43")

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is active_to.end_date
            assert context["funded"] == True

    @pytest.mark.skip(reason="Update later when CLINs are implemented")
    def test_expiring_and_unfunded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(portfolio=portfolio, number="42")

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
