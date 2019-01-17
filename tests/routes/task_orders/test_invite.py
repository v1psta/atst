import pytest
from flask import url_for

from tests.factories import PortfolioFactory, TaskOrderFactory


def test_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    to = TaskOrderFactory.create(portfolio=portfolio)
    response = client.post(
        url_for("task_orders.invite", task_order_id=to.id), follow_redirects=False
    )
    redirect = url_for(
        "portfolios.view_task_order", portfolio_id=to.portfolio_id, task_order_id=to.id
    )
    assert redirect in response.headers["Location"]
