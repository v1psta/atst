import pytest
from flask import url_for

from atst.domain.task_orders import TaskOrders
from atst.routes.task_orders.new import ShowTaskOrderWorkflow, UpdateTaskOrderWorkflow

from tests.factories import UserFactory, TaskOrderFactory, WorkspaceFactory


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


def test_show_task_order():
    workflow = ShowTaskOrderWorkflow()
    assert workflow.task_order is None
    task_order = TaskOrderFactory.create()
    another_workflow = ShowTaskOrderWorkflow(task_order_id=task_order.id)
    assert another_workflow.task_order == task_order


def test_show_task_order_formdata():
    task_order = TaskOrderFactory.create()
    workflow = ShowTaskOrderWorkflow(task_order_id=task_order.id)

    assert workflow.task_order.to_dictionary()["user_id"] is None
    assert workflow.task_order_formdata["user_id"] is ""
    for field in workflow.task_order_formdata:
        assert not field is None


def test_show_task_order_form():
    workflow = ShowTaskOrderWorkflow()
    assert not workflow.form.data["app_migration"]
    task_order = TaskOrderFactory.create()
    another_workflow = ShowTaskOrderWorkflow(task_order_id=task_order.id)
    assert (
        another_workflow.form.data["defense_component"] == task_order.defense_component
    )


def test_show_task_order_display_screen():
    task_order = TaskOrderFactory.create()
    workflow = ShowTaskOrderWorkflow(task_order_id=task_order.id)
    screens = workflow.display_screens
    # every form section is complete
    for i in range(2):
        assert screens[i]["complete"]
    # the review section is not
    assert not screens[3].get("complete")


def test_update_task_order_with_no_task_order():
    user = UserFactory.create()
    to_data = TaskOrderFactory.dictionary()
    workflow = UpdateTaskOrderWorkflow(to_data, user)
    assert workflow.task_order is None
    workflow.update()
    assert workflow.task_order
    assert workflow.task_order.scope == to_data["scope"]


def test_update_task_order_with_existing_task_order():
    user = UserFactory.create()
    task_order = TaskOrderFactory.create()
    to_data = serialize_dates(TaskOrderFactory.dictionary())
    workflow = UpdateTaskOrderWorkflow(
        to_data, user, screen=2, task_order_id=task_order.id
    )
    assert workflow.task_order.start_date != to_data["start_date"]
    workflow.update()
    assert workflow.task_order.start_date.strftime("%m/%d/%Y") == to_data["start_date"]


def test_invite_officers_to_task_order(queue):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=user)
    task_order = TaskOrderFactory.create(creator=user, workspace=workspace)
    to_data = {
        **TaskOrderFactory.dictionary(),
        "ko_invite": True,
        "cor_invite": True,
        "so_invite": True,
    }
    workflow = UpdateTaskOrderWorkflow(
        to_data, user, screen=3, task_order_id=task_order.id
    )
    workflow.update()
    workspace = task_order.workspace
    # owner and three officers are workspace members
    assert len(workspace.members) == 4
    roles = [member.role.name for member in workspace.members]
    # officers exist in roles
    assert roles.count("officer") == 3
    # email invitations are enqueued
    assert len(queue.get_queue()) == 3
    # task order has relationship to user for each officer role
    assert task_order.contracting_officer.dod_id == to_data["ko_dod_id"]
    assert task_order.contracting_officer_representative.dod_id == to_data["cor_dod_id"]
    assert task_order.security_officer.dod_id == to_data["so_dod_id"]


def test_add_officer_but_do_not_invite(queue):
    user = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=user)
    task_order = TaskOrderFactory.create(creator=user, workspace=workspace)
    to_data = {
        **TaskOrderFactory.dictionary(),
        "ko_invite": False,
        "cor_invite": False,
        "so_invite": False,
    }
    workflow = UpdateTaskOrderWorkflow(
        to_data, user, screen=3, task_order_id=task_order.id
    )
    workflow.update()
    workspace = task_order.workspace
    # owner is only workspace member
    assert len(workspace.members) == 1
    # no invitations are enqueued
    assert len(queue.get_queue()) == 0


def test_update_does_not_resend_invitation():
    user = UserFactory.create()
    contracting_officer = UserFactory.create()
    workspace = WorkspaceFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user,
        workspace=workspace,
        ko_first_name=contracting_officer.first_name,
        ko_last_name=contracting_officer.last_name,
        ko_dod_id=contracting_officer.dod_id,
    )
    to_data = {**task_order.to_dictionary(), "ko_invite": True}
    workflow = UpdateTaskOrderWorkflow(
        to_data, user, screen=3, task_order_id=task_order.id
    )
    for i in range(2):
        workflow.update()
    assert len(contracting_officer.invitations) == 1
