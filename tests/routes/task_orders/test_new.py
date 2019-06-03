import pytest
from flask import url_for

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models.attachment import Attachment
from atst.utils.localization import translate

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
)


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    attachment = Attachment(filename="sample_attachment", object_name="sample")

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_task_orders_new(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.get(url_for("task_orders.new", portfolio_id=portfolio.id))
    assert response.status_code == 200


def test_task_orders_create(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.post(
        url_for("task_orders.create", portfolio_id=portfolio.id),
        data={"number": "0123456789"},
    )
    assert response.status_code == 302


def test_task_orders_create_invalid_data(client, user_session, portfolio):
    user_session(portfolio.owner)
    num_task_orders = len(portfolio.task_orders)
    response = client.post(
        url_for("task_orders.create", portfolio_id=portfolio.id), data={"number": ""}
    )
    assert response.status_code == 200
    assert num_task_orders == len(portfolio.task_orders)
    assert "There were some errors" in response.data.decode()


def test_task_orders_edit():
    pass


def test_task_orders_update():
    pass


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_form_shows_errors(client, user_session, task_order):
    creator = task_order.creator
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data.update({"clin_01": "one milllllion dollars"})

    response = client.post(
        url_for("task_orders.update", screen=2, task_order_id=task_order.id),
        data=funding_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Not a valid decimal" in body


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_when_complete(client, user_session, task_order):
    pass


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_when_not_complete(client, user_session, task_order):
    pass


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_and_sign(client, user_session, task_order):
    pass
