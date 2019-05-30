import pytest

from atst.domain.task_orders import TaskOrders, TaskOrderError
from atst.domain.exceptions import UnauthorizedError
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolio_roles import PortfolioRoles
from atst.models.attachment import Attachment

from tests.factories import (
    TaskOrderFactory,
    UserFactory,
    PortfolioRoleFactory,
    PortfolioFactory,
)


@pytest.mark.skip(reason="Need to reimplement after new TO form is created")
def test_section_completion_status():
    dict_keys = [k for k in TaskOrders.SECTIONS.keys()]
    section = dict_keys[0]
    attrs = TaskOrders.SECTIONS[section].copy()
    attrs.remove("portfolio_name")
    task_order = TaskOrderFactory.create(**{k: None for k in attrs})
    leftover = attrs.pop()

    for attr in attrs:
        setattr(task_order, attr, "str12345")
    assert TaskOrders.section_completion_status(task_order, section) == "draft"

    setattr(task_order, leftover, "str12345")
    assert TaskOrders.section_completion_status(task_order, section) == "complete"


@pytest.mark.skip(reason="Need to reimplement after new TO form is created")
def test_all_sections_complete():
    task_order = TaskOrderFactory.create()
    attachment = Attachment(
        filename="sample_attachment",
        object_name="sample",
        resource="task_order",
        resource_id=task_order.id,
    )

    custom_attrs = {"csp_estimate": attachment}
    for attr_list in TaskOrders.SECTIONS.values():
        for attr in attr_list:
            if not getattr(task_order, attr):
                setattr(task_order, attr, custom_attrs.get(attr, "str12345"))

    task_order.scope = None
    assert not TaskOrders.all_sections_complete(task_order)
    task_order.scope = "str12345"
    assert TaskOrders.all_sections_complete(task_order)
