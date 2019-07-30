import pytest
from flask import url_for
from datetime import timedelta, date

from atst.domain.task_orders import TaskOrders
from atst.models.task_order import Status as TaskOrderStatus
from atst.models import TaskOrder

from tests.factories import CLINFactory, PortfolioFactory, TaskOrderFactory, UserFactory


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


@pytest.fixture
def completed_task_order():
    portfolio = PortfolioFactory.create()
    task_order = TaskOrderFactory.create(
        creator=portfolio.owner,
        portfolio=portfolio,
        create_clins=["1234567890123456789012345678901234567890123"],
    )

    return task_order


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_task_orders_form_step_one_add_pdf(client, user_session, portfolio):
    user_session(portfolio.owner)
    response = client.get(
        url_for("task_orders.form_step_one_add_pdf", portfolio_id=portfolio.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_one_add_pdf(
    client, user_session, portfolio, pdf_upload, session
):
    user_session(portfolio.owner)
    form_data = {"pdf": pdf_upload}
    response = client.post(
        url_for("task_orders.submit_form_step_one_add_pdf", portfolio_id=portfolio.id),
        data=form_data,
    )

    assert response.status_code == 302
    task_order = portfolio.task_orders[0]
    assert task_order.pdf.filename == pdf_upload.filename


def test_task_orders_form_step_one_add_pdf_existing_to(
    client, user_session, task_order
):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.form_step_one_add_pdf", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_one_add_pdf_existing_to(
    client, user_session, task_order, pdf_upload, pdf_upload2
):
    task_order.pdf = pdf_upload
    assert task_order.pdf.filename == pdf_upload.filename

    user_session(task_order.creator)
    form_data = {"pdf": pdf_upload2}
    response = client.post(
        url_for(
            "task_orders.submit_form_step_one_add_pdf", task_order_id=task_order.id
        ),
        data=form_data,
    )
    assert response.status_code == 302
    assert task_order.pdf.filename == pdf_upload2.filename


def test_task_orders_submit_form_step_one_add_pdf_delete_pdf(
    client, user_session, portfolio, pdf_upload
):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(pdf=pdf_upload, portfolio=portfolio)
    data = {"pdf": ""}
    response = client.post(
        url_for(
            "task_orders.submit_form_step_one_add_pdf", task_order_id=task_order.id
        ),
        data=data,
    )
    assert task_order.pdf is None
    assert response.status_code == 302


def test_task_orders_form_step_two_add_number(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.form_step_two_add_number", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_two_add_number(client, user_session, task_order):
    user_session(task_order.creator)
    form_data = {"number": "1234567890"}
    response = client.post(
        url_for(
            "task_orders.submit_form_step_two_add_number", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert task_order.number == "1234567890"


def test_task_orders_submit_form_step_two_add_number_existing_to(
    client, user_session, task_order
):
    user_session(task_order.creator)
    form_data = {"number": "0000000000"}
    original_number = task_order.number
    response = client.post(
        url_for(
            "task_orders.submit_form_step_two_add_number", task_order_id=task_order.id
        ),
        data=form_data,
    )
    assert response.status_code == 302
    assert task_order.number == "0000000000"
    assert task_order.number != original_number


def test_task_orders_form_step_three_add_clins(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.form_step_three_add_clins", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_task_orders_submit_form_step_three_add_clins(client, user_session, task_order):
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
        url_for(
            "task_orders.submit_form_step_three_add_clins", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 2


def test_task_orders_submit_form_step_three_add_clins_existing_to(
    client, user_session, task_order
):
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
        url_for(
            "task_orders.submit_form_step_three_add_clins", task_order_id=task_order.id
        ),
        data=form_data,
    )

    assert response.status_code == 302
    assert len(task_order.clins) == 1


def test_task_orders_form_step_four_review(client, user_session, completed_task_order):
    user_session(completed_task_order.creator)
    response = client.get(
        url_for(
            "task_orders.form_step_four_review", task_order_id=completed_task_order.id
        )
    )
    assert response.status_code == 200


def test_task_orders_form_step_four_review_incomplete_to(
    client, user_session, task_order
):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.form_step_four_review", task_order_id=task_order.id)
    )
    assert response.status_code == 404


def test_task_orders_form_step_five_confirm_signature(
    client, user_session, completed_task_order
):
    user_session(completed_task_order.creator)
    response = client.get(
        url_for(
            "task_orders.form_step_five_confirm_signature",
            task_order_id=completed_task_order.id,
        )
    )
    assert response.status_code == 200


def test_task_orders_form_step_five_confirm_signature_incomplete_to(
    client, user_session, task_order
):
    user_session(task_order.creator)
    response = client.get(
        url_for(
            "task_orders.form_step_five_confirm_signature", task_order_id=task_order.id
        )
    )
    assert response.status_code == 404


def test_task_orders_submit_task_order(client, user_session, task_order):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 302

    active_start_date = date.today() - timedelta(days=1)
    active_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=active_task_order, start_date=active_start_date)
    assert active_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=active_task_order.id)
    )
    assert active_task_order.status == TaskOrderStatus.ACTIVE

    upcoming_start_date = date.today() + timedelta(days=1)
    upcoming_task_order = TaskOrderFactory(portfolio=task_order.portfolio)
    CLINFactory(task_order=upcoming_task_order, start_date=upcoming_start_date)
    assert upcoming_task_order.status == TaskOrderStatus.UNSIGNED
    response = client.post(
        url_for("task_orders.submit_task_order", task_order_id=upcoming_task_order.id)
    )
    assert upcoming_task_order.status == TaskOrderStatus.UPCOMING


@pytest.mark.parametrize(
    "to_factory_args,expected_step",
    [
        ({"_pdf": None, "number": "", "clins": []}, "step_1"),
        ({"number": "", "clins": []}, "step_2"),
        ({"number": "1234567890123", "clins": []}, "step_3"),
        ({"number": "1234567890123", "create_clins": [1]}, "step_4"),
    ],
)
def test_task_orders_edit_redirects_to_latest_incomplete_step(
    client, user_session, portfolio, to_factory_args, expected_step
):
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, creator=portfolio.owner, **to_factory_args
    )
    user_session(portfolio.owner)

    response = client.get(url_for("task_orders.edit", task_order_id=task_order.id))

    assert expected_step in response.location


def test_can_cancel_edit_and_save_task_order(client, user_session, task_order, session):
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id, save=True),
        data={"number": "7896564324567"},
    )
    assert response.status_code == 302

    updated_task_order = session.query(TaskOrder).get(task_order.id)
    assert updated_task_order.number == "7896564324567"


def test_cancel_edit_does_not_save_invalid_form_input(client, user_session, session):
    task_order = TaskOrderFactory.create()
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id, save=True),
        data={"clins": "not really clins"},
    )
    assert response.status_code == 302

    # CLINs should be unchanged
    updated_task_order = session.query(TaskOrder).get(task_order.id)
    assert updated_task_order.clins == task_order.clins


def test_cancel_edit_without_saving(client, user_session, session):
    task_order = TaskOrderFactory.create(number=None)
    user_session(task_order.portfolio.owner)
    response = client.post(
        url_for("task_orders.cancel_edit", task_order_id=task_order.id),
        data={"number": "7643906432984"},
    )
    assert response.status_code == 302

    # TO number should be unchanged
    updated_task_order = session.query(TaskOrder).get(task_order.id)
    assert updated_task_order.number is None


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
