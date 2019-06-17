from datetime import date
from flask import url_for
import pytest
from datetime import timedelta, date

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models import *
from atst.models.portfolio_role import Status as PortfolioStatus
from atst.models.task_order import Status as TaskOrderStatus
from atst.utils.localization import translate

from tests.factories import *
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


def test_review_task_order_not_draft(client, user_session, task_order):
    TaskOrders.sign(task_order=task_order, signer_dod_id=random_dod_id())
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.review_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_review_task_order_draft(client, user_session, task_order):
    TaskOrders.update(
        task_order_id=task_order.id, number="1234567890", clins=[], pdf=None
    )
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.review_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 302
    assert url_for("task_orders.edit", task_order_id=task_order.id) in response.location


def test_submit_task_order(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 302

    active_start_date = date.today() - timedelta(days=1)
    active_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=active_task_order, start_date=active_start_date)
    assert active_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=active_task_order.id)
    )
    assert active_task_order.status == TaskOrderStatus.ACTIVE

    upcoming_start_date = date.today() + timedelta(days=1)
    upcoming_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=upcoming_task_order, start_date=upcoming_start_date)
    assert upcoming_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=upcoming_task_order.id)
    )
    assert upcoming_task_order.status == TaskOrderStatus.UPCOMING


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
