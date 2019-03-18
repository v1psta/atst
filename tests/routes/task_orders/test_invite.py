import pytest
from flask import url_for

from tests.factories import PortfolioFactory, TaskOrderFactory, UserFactory


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


def test_invite_officers_to_task_order(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        ko_invite=True, cor_invite=True, so_invite=True
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    # owner and three officers are portfolio members
    assert len(portfolio.members) == 4
    # email invitations are enqueued
    assert len(queue.get_queue()) == 3
    # task order has relationship to user for each officer role
    assert task_order.contracting_officer.dod_id == task_order.ko_dod_id
    assert task_order.contracting_officer_representative.dod_id == task_order.cor_dod_id
    assert task_order.security_officer.dod_id == task_order.so_dod_id


def test_add_officer_but_do_not_invite(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        ko_invite=False, cor_invite=False, so_invite=False
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    portfolio = task_order.portfolio
    # owner is only portfolio member
    assert len(portfolio.members) == 1
    # no invitations are enqueued
    assert len(queue.get_queue()) == 0


def test_does_not_resend_officer_invitation(client, user_session):
    user = UserFactory.create()
    contracting_officer = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user,
        portfolio=portfolio,
        ko_first_name=contracting_officer.first_name,
        ko_last_name=contracting_officer.last_name,
        ko_dod_id=contracting_officer.dod_id,
        ko_invite=True,
    )

    user_session(user)
    for i in range(2):
        client.post(url_for("task_orders.invite", task_order_id=task_order.id))
    assert len(contracting_officer.invitations) == 1


def test_does_not_invite_if_task_order_incomplete(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        scope=None, ko_invite=True, cor_invite=True, so_invite=True
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    response = client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    # redirected to review screen
    assert response.headers["Location"] == url_for(
        "task_orders.new", screen=4, task_order_id=task_order.id, _external=True
    )
    # only owner is portfolio member
    assert len(portfolio.members) == 1
    # no email invitations are enqueued
    assert len(queue.get_queue()) == 0
