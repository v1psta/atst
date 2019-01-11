import pytest
from flask import url_for

from tests.factories import TaskOrderFactory


def test_invite(client):
    to = TaskOrderFactory.create()
    response = client.post(
        url_for("task_orders.invite", task_order_id=to.id), follow_redirects=False
    )
