import pytest
from flask import url_for

from atst.database import db
from atst.models.workspace import Workspace

from tests.factories import UserFactory, WorkspaceFactory, TaskOrderFactory


def test_edit_task_order(client, user_session):
    creator = UserFactory.create()
    task_order = TaskOrderFactory.create(
        creator=creator, workspace=WorkspaceFactory.create()
    )
    user_session()
    response = client.get(url_for("task_orders.edit", task_order_id=task_order.id))
    assert response.status_code == 200


def test_create_new_workspace(client, user_session):
    creator = UserFactory.create()
    task_order = TaskOrderFactory.create(
        creator=creator, workspace=WorkspaceFactory.create()
    )
    user_session()

    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id),
        data={
            "clin_0001": 12345,
            "clin_0003": 12345,
            "clin_1001": 12345,
            "clin_1003": 12345,
            "clin_2001": 12345,
            "clin_2003": 12345,
        },
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert task_order.clin_0001 == 12345
