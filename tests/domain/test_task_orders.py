import pytest

from atst.domain.task_orders import TaskOrders, TaskOrderError

from tests.factories import TaskOrderFactory, UserFactory


def test_is_section_complete():
    dict_keys = [k for k in TaskOrders.SECTIONS.keys()]
    section = dict_keys[0]
    attrs = TaskOrders.SECTIONS[section].copy()
    task_order = TaskOrderFactory.create(**{k: None for k in attrs})
    leftover = attrs.pop()
    for attr in attrs:
        setattr(task_order, attr, "str12345")
    assert not TaskOrders.is_section_complete(task_order, section)
    setattr(task_order, leftover, "str12345")
    assert TaskOrders.is_section_complete(task_order, section)


def test_all_sections_complete():
    task_order = TaskOrderFactory.create()
    for attr_list in TaskOrders.SECTIONS.values():
        for attr in attr_list:
            if not getattr(task_order, attr):
                setattr(task_order, attr, "str12345")

    task_order.scope = None
    assert not TaskOrders.all_sections_complete(task_order)
    task_order.scope = "str12345"
    assert TaskOrders.all_sections_complete(task_order)


def test_add_officer():
    task_order = TaskOrderFactory.create()
    ko = UserFactory.create()
    owner = task_order.workspace.owner
    TaskOrders.add_officer(owner, task_order, "contracting_officer", ko.to_dictionary())

    assert task_order.contracting_officer == ko
    workspace_users = [ws_role.user for ws_role in task_order.workspace.members]
    assert ko in workspace_users


def test_add_officer_with_nonexistent_role():
    task_order = TaskOrderFactory.create()
    ko = UserFactory.create()
    owner = task_order.workspace.owner
    with pytest.raises(TaskOrderError):
        TaskOrders.add_officer(owner, task_order, "pilot", ko.to_dictionary())


def test_add_officer_who_is_already_workspace_member():
    task_order = TaskOrderFactory.create()
    owner = task_order.workspace.owner
    TaskOrders.add_officer(
        owner, task_order, "contracting_officer", owner.to_dictionary()
    )

    assert task_order.contracting_officer == owner
    member = task_order.workspace.members[0]
    assert member.user == owner and member.role_name == "owner"
