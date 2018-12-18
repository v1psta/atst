import pytest
from flask import url_for

from atst.database import db
from atst.models.workspace import Workspace

from tests.factories import UserFactory, WorkspaceFactory, TaskOrderFactory


def test_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session()
    response = client.get(url_for("task_orders.new", screen=1))
    assert response.status_code == 200


def test_create_new_task_order(client, user_session):
    creator = UserFactory.create()
    task_order = TaskOrderFactory.create(
        creator=creator, workspace=WorkspaceFactory.create()
    )
    user_session()

    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id),
        data={**TaskOrderFactory.dictionary(), "clin_01": 12345, "clin_03": 12345},
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert task_order.clin_01 == 12345
