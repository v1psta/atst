import pytest
from flask import url_for

from atst.domain.task_orders import TaskOrders
from atst.domain.permission_sets import PermissionSets
from atst.models.attachment import Attachment
from atst.routes.task_orders.new import ShowTaskOrderWorkflow, UpdateTaskOrderWorkflow
from atst.utils.localization import translate

from tests.factories import (
    UserFactory,
    TaskOrderFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
)


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


class TestShowTaskOrderWorkflow:
    def test_portfolio_when_task_order_exists(self):
        portfolio = PortfolioFactory.create()
        task_order = TaskOrderFactory(portfolio=portfolio)
        assert portfolio.num_task_orders > 0

        workflow = ShowTaskOrderWorkflow(
            user=task_order.creator, task_order_id=task_order.id
        )
        assert portfolio == workflow.portfolio

    def test_portfolio_with_portfolio_id(self):
        user = UserFactory.create()
        portfolio = PortfolioFactory.create(owner=user)
        workflow = ShowTaskOrderWorkflow(
            user=portfolio.owner, portfolio_id=portfolio.id
        )
        assert portfolio == workflow.portfolio


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


def test_new_to_can_edit_pf_attributes_screen_1():
    portfolio = PortfolioFactory.create()
    workflow = ShowTaskOrderWorkflow(user=portfolio.owner)
    assert not workflow.pf_attributes_read_only


def test_new_pf_can_edit_pf_attributes_on_back_navigation():
    portfolio = PortfolioFactory.create()
    pf_task_order = TaskOrderFactory(portfolio=portfolio)
    pf_workflow = ShowTaskOrderWorkflow(
        user=pf_task_order.creator, task_order_id=pf_task_order.id
    )
    assert not pf_workflow.pf_attributes_read_only


def test_to_on_pf_cannot_edit_pf_attributes():
    portfolio = PortfolioFactory.create()
    pf_task_order = TaskOrderFactory(portfolio=portfolio)

    workflow = ShowTaskOrderWorkflow(user=portfolio.owner, portfolio_id=portfolio.id)
    assert portfolio.num_task_orders == 1
    assert workflow.pf_attributes_read_only

    second_task_order = TaskOrderFactory(portfolio=portfolio)
    second_workflow = ShowTaskOrderWorkflow(
        user=portfolio.owner, task_order_id=second_task_order.id
    )
    assert portfolio.num_task_orders > 1
    assert second_workflow.pf_attributes_read_only


@pytest.mark.skip(reason="Reimplement after TO form is updated")
def test_create_new_task_order(client, user_session, pdf_upload):
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

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(created_task_order_id)
    assert created_task_order.portfolio is not None

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


def test_create_new_task_order_for_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    creator = portfolio.owner
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    app_info_data = slice_data_for_section(task_order_data, "app_info")
    app_info_data["portfolio_name"] = portfolio.name

    response = client.post(
        url_for("task_orders.update", screen=1, portfolio_id=portfolio.id),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(created_task_order_id)
    assert created_task_order.portfolio_name == portfolio.name
    assert created_task_order.portfolio == portfolio


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_task_order_form_shows_errors(client, user_session, task_order):
    creator = task_order.creator
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data.update({"clin_01": "one milllllion dollars"})

    response = client.post(
        url_for("task_orders.update", screen=2, task_order_id=task_order.id),
        data=funding_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Not a valid decimal" in body


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_review_screen_when_all_sections_complete(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.new", screen=4, task_order_id=task_order.id)
    )

    body = response.data.decode()
    assert translate("task_orders.form.draft_alert_title") not in body
    assert response.status_code == 200


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_review_screen_when_not_all_sections_complete(client, user_session, task_order):
    TaskOrders.update(task_order, clin_01=None)
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.new", screen=4, task_order_id=task_order.id)
    )

    body = response.data.decode()
    assert translate("task_orders.form.draft_alert_title") in body
    assert response.status_code == 200


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    attachment = Attachment(filename="sample_attachment", object_name="sample")

    return TaskOrderFactory.create(creator=user, portfolio=portfolio)


def test_show_task_order(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator)
    assert workflow.task_order is None
    another_workflow = ShowTaskOrderWorkflow(
        task_order.creator, task_order_id=task_order.id
    )
    assert another_workflow.task_order == task_order


def test_show_task_order_display_screen(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator, task_order_id=task_order.id)
    screens = workflow.display_screens
    # every form section is complete
    for i in range(2):
        assert screens[i]["completion"] == "complete"
    # the review section is not
    assert screens[3]["completion"] == "incomplete"


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_update_task_order_with_existing_task_order(task_order):
    to_data = serialize_dates(TaskOrderFactory.dictionary())
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, screen=2, task_order_id=task_order.id
    )
    assert workflow.task_order.start_date != to_data["start_date"]
    workflow.update()
    assert workflow.task_order.start_date.strftime("%m/%d/%Y") == to_data["start_date"]


@pytest.mark.skip(reason="Update after implementing new TO form")
def test_review_task_order_form(client, user_session, task_order):
    user_session(task_order.creator)

    for idx, section in enumerate(TaskOrders.SECTIONS):
        response = client.get(
            url_for("task_orders.new", screen=idx + 1, task_order_id=task_order.id)
        )

        assert response.status_code == 200


@pytest.mark.skip(reason="Reimplement after TO form is updated")
def test_mo_redirected_to_build_page(client, user_session, portfolio):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200
