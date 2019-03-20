from flask import url_for

from atst.domain.task_orders import TaskOrders
from tests.factories import (
    UserFactory,
    TaskOrderFactory,
    PortfolioFactory,
    DD254Factory,
)


def create_ko_task_order(user_session, contracting_officer):
    portfolio = PortfolioFactory.create(owner=contracting_officer)
    user_session(contracting_officer)

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=contracting_officer
    )

    TaskOrders.add_officer(
        task_order, "contracting_officer", contracting_officer.to_dictionary()
    )

    dd_254 = DD254Factory.create()
    TaskOrders.add_dd_254(task_order, dd_254.to_dictionary())

    return task_order


def test_show_signature_requested_not_ko(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)
    TaskOrders.update(task_order, contracting_officer=None)

    response = client.get(
        url_for("task_orders.signature_requested", task_order_id=task_order.id)
    )

    assert response.status_code == 404


def test_show_signature_requested(client, user_session):
    contracting_officer = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=contracting_officer)
    user_session(contracting_officer)

    # create unfinished TO
    task_order = TaskOrderFactory.create(portfolio=portfolio, clin_01=None)
    TaskOrders.add_officer(
        task_order, "contracting_officer", contracting_officer.to_dictionary()
    )
    response = client.get(
        url_for("task_orders.signature_requested", task_order_id=task_order.id)
    )
    assert response.status_code == 404

    # Finish TO
    TaskOrders.update(task_order, clin_01=100)
    response = client.get(
        url_for("task_orders.signature_requested", task_order_id=task_order.id)
    )
    assert response.status_code == 404

    # Complete DD 254
    dd_254 = DD254Factory.create()
    TaskOrders.add_dd_254(task_order, dd_254.to_dictionary())
    response = client.get(
        url_for("task_orders.signature_requested", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_show_signature_requested_already_signed(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)
    TaskOrders.update(task_order, signer_dod_id=contracting_officer.dod_id)

    response = client.get(
        url_for("task_orders.signature_requested", task_order_id=task_order.id)
    )

    assert response.status_code == 404


def test_signing_task_order_not_ko(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)
    TaskOrders.update(task_order, contracting_officer=None)

    response = client.post(
        url_for("task_orders.record_signature", task_order_id=task_order.id), data={}
    )

    assert response.status_code == 404


def test_singing_an_already_signed_task_order(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)
    TaskOrders.update(task_order, signer_dod_id=contracting_officer.dod_id)

    response = client.post(
        url_for("task_orders.record_signature", task_order_id=task_order.id),
        data={"signature": "y", "level_of_warrant": "33.33"},
    )

    assert response.status_code == 404


def test_signing_a_task_order(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)

    assert task_order.signed_at is None
    assert task_order.signer_dod_id is None

    response = client.post(
        url_for("task_orders.record_signature", task_order_id=task_order.id),
        data={"signature": "y", "level_of_warrant": "33.33"},
    )

    assert (
        url_for(
            "portfolios.view_task_order",
            portfolio_id=task_order.portfolio_id,
            task_order_id=task_order.id,
        )
        in response.headers["Location"]
    )

    assert task_order.signer_dod_id == contracting_officer.dod_id
    assert task_order.signed_at is not None


def test_signing_a_task_order_failure(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)

    response = client.post(
        url_for("task_orders.record_signature", task_order_id=task_order.id),
        data={"level_of_warrant": "33.33"},
    )

    assert response.status_code == 400


def test_signing_a_task_order_unlimited_level_of_warrant(client, user_session):
    contracting_officer = UserFactory.create()
    task_order = create_ko_task_order(user_session, contracting_officer)

    assert task_order.signed_at is None
    assert task_order.signer_dod_id is None

    response = client.post(
        url_for("task_orders.record_signature", task_order_id=task_order.id),
        data={
            "signature": "y",
            "level_of_warrant": "33.33",
            "unlimited_level_of_warrant": "y",
        },
    )

    assert (
        url_for(
            "portfolios.view_task_order",
            portfolio_id=task_order.portfolio_id,
            task_order_id=task_order.id,
        )
        in response.headers["Location"]
    )

    assert task_order.signed_at is not None
    assert task_order.signer_dod_id == contracting_officer.dod_id
    assert task_order.unlimited_level_of_warrant == True
    assert task_order.level_of_warrant == None
