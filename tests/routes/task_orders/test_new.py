import pytest
from flask import url_for

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models import Attachment, TaskOrder
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

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_task_orders_add_pdf(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.get(url_for("task_orders.add_pdf", portfolio_id=portfolio.id))
    assert response.status_code == 200


def test_task_orders_upload_pdf(client, user_session, portfolio, pdf_upload, session):
    user_session(portfolio.owner)
    form_data = {"pdf": pdf_upload}
    response = client.post(
        url_for("task_orders.upload_pdf", portfolio_id=portfolio.id), data=form_data
    )

    assert response.status_code == 302
    task_order = portfolio.task_orders[0]
    assert task_order.pdf.filename == pdf_upload.filename


def test_task_orders_add_number(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.add_number", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_update_number(client, user_session, task_order):
    user_session(task_order.creator)
    form_data = {"number": "1234567890"}
    response = client.post(
        url_for("task_orders.update_number", task_order_id=task_order.id),
        data=form_data,
    )

    assert response.status_code == 302
    assert task_order.number == "1234567890"


def test_task_orders_add_clins(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(url_for("task_orders.add_clins", task_order_id=task_order.id))
    assert response.status_code == 200


def test_task_orders_update_clins(client, user_session, task_order):
    user_session(task_order.creator)
    form_data = {
        "clins-0-jedi_clin_type": "JEDI_CLIN_1",
        "clins-0-clin_number": "12312",
        "clins-0-start_date": "01/01/2020",
        "clins-0-end_date": "01/01/2021",
        "clins-0-obligated_amount": "5000",
        "clins-0-loas-0": "123123123123",
        "clins-0-loas-1": "345345234",
        "clins-1-jedi_clin_type": "JEDI_CLIN_1",
        "clins-1-number": "12312",
        "clins-1-start_date": "01/01/2020",
        "clins-1-end_date": "01/01/2021",
        "clins-1-obligated_amount": "5000",
        "clins-1-loas-0": "78979087",
    }
    response = client.post(
        url_for("task_orders.update_clins", task_order_id=task_order.id), data=form_data
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 2


def test_task_orders_review(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(url_for("task_orders.review", task_order_id=task_order.id))
    assert response.status_code == 200


def test_task_orders_confirm_signature(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.confirm_signature", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_form_step_one_add_pdf_existing_to(
    client, user_session, task_order
):
    user_session(task_order.creator)
    response = client.get(url_for("task_orders.add_pdf", task_order_id=task_order.id))
    assert response.status_code == 200


def test_task_orders_upload_pdf_existing_to(
    client, user_session, task_order, pdf_upload, pdf_upload2
):
    task_order.pdf = pdf_upload
    assert task_order.pdf.filename == pdf_upload.filename

    user_session(task_order.creator)
    form_data = {"pdf": pdf_upload2}
    response = client.post(
        url_for("task_orders.upload_pdf", task_order_id=task_order.id), data=form_data
    )
    assert response.status_code == 302
    assert task_order.pdf.filename == pdf_upload2.filename


def test_task_orders_upload_pdf_delete_pdf(client, user_session, portfolio, pdf_upload):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(pdf=pdf_upload, portfolio=portfolio)
    data = {"pdf": ""}
    response = client.post(
        url_for("task_orders.upload_pdf", task_order_id=task_order.id), data=data
    )
    assert task_order.pdf is None
    assert response.status_code == 302


def test_task_orders_update_number_existing_to(client, user_session, task_order):
    user_session(task_order.creator)
    form_data = {"number": "0000000000"}
    original_number = task_order.number
    response = client.post(
        url_for("task_orders.update_number", task_order_id=task_order.id),
        data=form_data,
    )
    assert response.status_code == 302
    assert task_order.number == "0000000000"
    assert task_order.number != original_number


def test_task_orders_update_clins_existing_to(client, user_session, task_order):
    clin_list = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": "01/01/2020",
            "end_date": "01/01/2021",
            "obligated_amount": "5000",
            "loas": ["123123123123", "345345234"],
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": "01/01/2020",
            "end_date": "01/01/2021",
            "obligated_amount": "5000",
            "loas": ["78979087"],
        },
    ]
    TaskOrders.create_clins(task_order.id, clin_list)
    assert len(task_order.clins) == 2

    user_session(task_order.creator)
    form_data = {
        "clins-0-jedi_clin_type": "JEDI_CLIN_1",
        "clins-0-clin_number": "12312",
        "clins-0-start_date": "01/01/2020",
        "clins-0-end_date": "01/01/2021",
        "clins-0-obligated_amount": "5000",
        "clins-0-loas-0": "123123123123",
    }
    response = client.post(
        url_for("task_orders.update_clins", task_order_id=task_order.id), data=form_data
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 1


@pytest.mark.skip(reason="Reevaluate how form handles invalid data")
def test_task_orders_update_invalid_data(client, user_session, portfolio):
    user_session(portfolio.owner)
    num_task_orders = len(portfolio.task_orders)
    response = client.post(
        url_for("task_orders.update", portfolio_id=portfolio.id), data={"number": ""}
    )
    assert response.status_code == 400
    assert num_task_orders == len(portfolio.task_orders)
    assert "There were some errors" in response.data.decode()


@pytest.mark.skip(reason="Reevaluate if user can see review page w/ incomplete TO")
def test_cannot_get_to_review_screen_with_incomplete_data(
    client, user_session, portfolio
):
    user_session(portfolio.owner)
    data = {"number": "0123456789"}
    response = client.post(
        url_for("task_orders.update", portfolio_id=portfolio.id, review=True), data=data
    )
    assert response.status_code == 400


@pytest.mark.skip(reason="Update after implementing errors on TO form")
def test_task_order_form_shows_errors(client, user_session, task_order):
    creator = task_order.creator
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data.update({"clin_01": "one milllllion dollars"})

    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id),
        data=funding_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Not a valid decimal" in body
