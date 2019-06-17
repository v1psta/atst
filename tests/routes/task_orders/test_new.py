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
    attachment = Attachment(filename="sample_attachment", object_name="sample")

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_task_orders_edit(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.get(url_for("task_orders.edit", portfolio_id=portfolio.id))
    assert response.status_code == 200


def test_task_orders_update(client, user_session, portfolio):
    user_session(portfolio.owner)
    form_data = {
        "number": "0123456789",
        "pdf": pdf_upload,
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
        url_for("task_orders.update", portfolio_id=portfolio.id), data=form_data
    )
    assert response.status_code == 302
    task_order = session.query(TaskOrder).filter_by(number=data["number"]).one()
    assert task_order.pdf.filename == pdf_upload.filename


def test_task_orders_edit_existing_to(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(url_for("task_orders.edit", task_order_id=task_order.id))
    assert response.status_code == 200


def test_task_orders_update_existing_to(client, user_session, task_order):
    user_session(task_order.creator)
    form_data = {
        "number": "0123456789",
        "clins-0-jedi_clin_type": "JEDI_CLIN_1",
        "clins-0-number": "12312",
        "clins-0-start_date": "01/01/2020",
        "clins-0-end_date": "01/01/2021",
        "clins-0-obligated_amount": "5000",
        "clins-0-loas-0": "123123123123",
    }
    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id), data=form_data
    )
    assert response.status_code == 302
    assert task_order.number == "0123456789"


def test_task_orders_update_invalid_data(client, user_session, portfolio):
    user_session(portfolio.owner)
    num_task_orders = len(portfolio.task_orders)
    response = client.post(
        url_for("task_orders.update", portfolio_id=portfolio.id), data={"number": ""}
    )
    assert response.status_code == 400
    assert num_task_orders == len(portfolio.task_orders)
    assert "There were some errors" in response.data.decode()


def test_task_orders_update(client, user_session, portfolio, pdf_upload):
    user_session(portfolio.owner)
    data = {"number": "0123456789", "pdf": pdf_upload}
    task_order = TaskOrderFactory.create(number="0987654321", portfolio=portfolio)
    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id), data=data
    )
    assert task_order.number == data["number"]
    assert response.status_code == 400


def test_task_orders_update_pdf(
    client, user_session, portfolio, pdf_upload, pdf_upload2
):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(pdf=pdf_upload, portfolio=portfolio)
    data = {"number": "0123456789", "pdf": pdf_upload2}
    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id), data=data
    )
    assert task_order.pdf.filename == pdf_upload2.filename
    assert response.status_code == 400


def test_task_orders_update_delete_pdf(client, user_session, portfolio, pdf_upload):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(pdf=pdf_upload, portfolio=portfolio)
    data = {"number": "0123456789", "pdf": ""}
    response = client.post(
        url_for("task_orders.update", task_order_id=task_order.id), data=data
    )
    assert task_order.pdf is None
    assert response.status_code == 400


def test_cannot_get_to_review_screen_with_incomplete_data(
    client, user_session, portfolio
):
    user_session(portfolio.owner)
    data = {"number": "0123456789"}
    response = client.post(
        url_for("task_orders.update", portfolio_id=portfolio.id, review=True), data=data
    )
    assert response.status_code == 400


@pytest.mark.skip(reason="Update after implementing new TO form")
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


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_when_complete(client, user_session, task_order):
    pass


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_when_not_complete(client, user_session, task_order):
    pass


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_review_and_sign(client, user_session, task_order):
    pass
