import pytest
from flask import url_for

from atst.domain.task_orders import TaskOrders
from atst.models.attachment import Attachment
from atst.routes.task_orders.new import ShowTaskOrderWorkflow, UpdateTaskOrderWorkflow
from atst.utils.localization import translate

from tests.factories import UserFactory, TaskOrderFactory, PortfolioFactory


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
    assert not workflow.pf_attributes_read_only()


def test_new_pf_can_edit_pf_attributes_on_back_navigation():
    portfolio = PortfolioFactory.create()
    pf_task_order = TaskOrderFactory(portfolio=portfolio)
    pf_workflow = ShowTaskOrderWorkflow(
        user=pf_task_order.creator, task_order_id=pf_task_order.id
    )
    assert not pf_workflow.pf_attributes_read_only()


def test_to_on_pf_cannot_edit_pf_attributes():
    portfolio = PortfolioFactory.create()
    pf_task_order = TaskOrderFactory(portfolio=portfolio)

    workflow = ShowTaskOrderWorkflow(user=portfolio.owner, portfolio_id=portfolio.id)
    assert portfolio.num_task_orders == 1
    assert workflow.pf_attributes_read_only()

    second_task_order = TaskOrderFactory(portfolio=portfolio)
    second_workflow = ShowTaskOrderWorkflow(
        user=portfolio.owner, task_order_id=second_task_order.id
    )
    assert portfolio.num_task_orders > 1
    assert second_workflow.pf_attributes_read_only()


# TODO: this test will need to be more complicated when we add validation to
# the forms
def test_create_new_task_order(client, user_session, pdf_upload):
    creator = UserFactory.create()
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    app_info_data = slice_data_for_section(task_order_data, "app_info")
    portfolio_name = "Mos Eisley"
    defense_component = "Defense Health Agency"
    app_info_data["portfolio_name"] = portfolio_name
    app_info_data["defense_component"] = defense_component

    response = client.post(
        url_for("task_orders.update", screen=1),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(creator, created_task_order_id)
    assert created_task_order.portfolio is not None
    assert created_task_order.portfolio.name == portfolio_name
    assert created_task_order.portfolio.defense_component == defense_component

    funding_data = slice_data_for_section(task_order_data, "funding")
    funding_data = serialize_dates(funding_data)
    funding_data["csp_estimate"] = pdf_upload
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
    app_info_data["defense_component"] = portfolio.defense_component

    response = client.post(
        url_for("task_orders.update", screen=1, portfolio_id=portfolio.id),
        data=app_info_data,
        follow_redirects=False,
    )
    assert url_for("task_orders.new", screen=2) in response.headers["Location"]

    created_task_order_id = response.headers["Location"].split("/")[-1]
    created_task_order = TaskOrders.get(creator, created_task_order_id)
    assert created_task_order.portfolio_name == portfolio.name
    assert created_task_order.defense_component == portfolio.defense_component
    assert created_task_order.portfolio == portfolio


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


def test_task_order_validates_email_address(client, user_session, task_order):
    creator = task_order.creator
    user_session(creator)

    task_order_data = TaskOrderFactory.dictionary()
    oversight_data = slice_data_for_section(task_order_data, "oversight")
    oversight_data.update({"ko_email": "not an email"})

    response = client.post(
        url_for("task_orders.update", screen=3, task_order_id=task_order.id),
        data=oversight_data,
        follow_redirects=False,
    )

    body = response.data.decode()
    assert "There were some errors" in body
    assert "Invalid email" in body


def test_review_screen_when_all_sections_complete(client, user_session, task_order):
    user_session(task_order.creator)
    response = client.get(
        url_for("task_orders.new", screen=4, task_order_id=task_order.id)
    )

    body = response.data.decode()
    assert translate("task_orders.form.draft_alert_title") not in body
    assert response.status_code == 200


def test_review_screen_when_not_all_sections_complete(client, user_session, task_order):
    TaskOrders.update(task_order.creator, task_order, clin_01=None)
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

    return TaskOrderFactory.create(
        creator=user, portfolio=portfolio, csp_estimate=attachment
    )


def test_show_task_order(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator)
    assert workflow.task_order is None
    another_workflow = ShowTaskOrderWorkflow(
        task_order.creator, task_order_id=task_order.id
    )
    assert another_workflow.task_order == task_order


def test_show_task_order_form_list_data():
    complexity = ["oconus", "tactical_edge"]
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user, portfolio=portfolio, complexity=complexity
    )
    workflow = ShowTaskOrderWorkflow(user, task_order_id=task_order.id)

    assert workflow.form.complexity.data == complexity


def test_show_task_order_form(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator)
    assert not workflow.form.data["app_migration"]
    another_workflow = ShowTaskOrderWorkflow(
        task_order.creator, task_order_id=task_order.id
    )
    assert (
        another_workflow.form.data["defense_component"] == task_order.defense_component
    )


def test_show_task_order_display_screen(task_order):
    workflow = ShowTaskOrderWorkflow(task_order.creator, task_order_id=task_order.id)
    screens = workflow.display_screens
    # every form section is complete
    for i in range(2):
        assert screens[i]["completion"] == "complete"
    # the review section is not
    assert screens[3]["completion"] == "incomplete"


def test_update_task_order_with_no_task_order():
    user = UserFactory.create()
    to_data = TaskOrderFactory.dictionary()
    workflow = UpdateTaskOrderWorkflow(user, to_data)
    assert workflow.task_order is None
    workflow.update()
    assert workflow.task_order
    assert workflow.task_order.scope == to_data["scope"]


def test_update_task_order_with_existing_task_order(task_order):
    to_data = serialize_dates(TaskOrderFactory.dictionary())
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, screen=2, task_order_id=task_order.id
    )
    assert workflow.task_order.start_date != to_data["start_date"]
    workflow.update()
    assert workflow.task_order.start_date.strftime("%m/%d/%Y") == to_data["start_date"]


def test_update_to_redirects_to_ko_review(client, user_session, task_order):
    ko = UserFactory.create()
    task_order.contracting_officer = ko
    user_session(ko)
    url = url_for(
        "portfolios.ko_review",
        portfolio_id=task_order.portfolio.id,
        task_order_id=task_order.id,
    )
    response = client.post(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id, next=url)
    )
    body = response.data.decode()

    assert url in body
    assert response.status_code == 302


def test_other_text_not_saved_if_other_not_checked(task_order):
    to_data = {
        **TaskOrderFactory.dictionary(),
        "complexity": ["conus"],
        "complexity_other": "quite complex",
    }
    workflow = UpdateTaskOrderWorkflow(
        task_order.creator, to_data, task_order_id=task_order.id
    )
    workflow.update()
    assert not workflow.task_order.complexity_other


def test_cor_data_set_to_user_data_if_am_cor_is_checked(task_order):
    to_data = {**task_order.to_dictionary(), "am_cor": True}
    workflow = UpdateTaskOrderWorkflow(task_order.creator, to_data, 3, task_order.id)
    workflow.update()
    assert task_order.cor_dod_id == task_order.creator.dod_id


def test_review_task_order_form(client, user_session, task_order):
    user_session(task_order.creator)

    for idx, section in enumerate(TaskOrders.SECTIONS):
        response = client.get(
            url_for("task_orders.new", screen=idx + 1, task_order_id=task_order.id)
        )

        assert response.status_code == 200
