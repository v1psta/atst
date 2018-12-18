import pytest

from atst.domain.task_orders import TaskOrders

from tests.factories import TaskOrderFactory


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
