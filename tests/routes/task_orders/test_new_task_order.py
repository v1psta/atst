import pytest
from flask import url_for

from atst.domain.task_orders import TaskOrders

from tests.factories import UserFactory, TaskOrderFactory


def test_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session()
    response = client.get(url_for("task_orders.new", screen=1))
    assert response.status_code == 200


def post_to_task_order_step(client, data, screen, task_order_id=None):
    return client.post(
        url_for("task_orders.update", screen=screen, task_order_id=task_order_id),
        data=data,
        follow_redirects=False,
    )


def slice_data_for_section(task_order_data, section):
    attrs = TaskOrders.SECTIONS[section]
    return {k: v for k, v in task_order_data.items() if k in attrs}


def serialize_dates(data):
    if not data:
        return data

    dates = {
        k: v.strftime("%m/%d/%Y") for k, v in data.items() if hasattr(v, "strftime")
    }

    data.update(dates)

    return data


# TODO: this test will need to be more complicated when we add validation to
# the forms
def test_create_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    app_info_data = slice_data_for_section(task_order_data, "app_info")

    response = client.post(
        url_for("task_orders.update", screen=1),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    response = client.post(
        response.headers["Location"], data=funding_data, follow_redirects=False
    )
    assert url_for("task_orders.new", screen=3) in response.headers["Location"]

    oversight_data = slice_data_for_section(task_order_data, "oversight")
    response = client.post(
        response.headers["Location"], data=oversight_data, follow_redirects=False
    )
    assert url_for("task_orders.new", screen=4) in response.headers["Location"]
