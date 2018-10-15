from atst.domain.reports import Reports

from tests.factories import RequestFactory, TaskOrderFactory, WorkspaceFactory

CLIN_NUMS = ["0001", "0003", "1001", "1003", "2001", "2003"]


def test_workspace_totals():
    task_order = TaskOrderFactory.create()

    for num in CLIN_NUMS:
        setattr(task_order, "clin_{}".format(num), 200)

    request = RequestFactory.create(task_order=task_order)
    workspace = WorkspaceFactory.create(request=request)
    report = Reports.workspace_totals(workspace)
    total = 200 * len(CLIN_NUMS)
    assert report == {"budget": total, "spent": 0}


# this is sketched in until we do real reporting
def test_monthly_totals():
    request = RequestFactory.create()
    workspace = WorkspaceFactory.create(request=request)
    monthly = Reports.monthly_totals(workspace)

    assert not monthly["environments"]
    assert not monthly["projects"]
    assert not monthly["workspace"]


# this is sketched in until we do real reporting
def test_cumulative_budget():
    request = RequestFactory.create()
    workspace = WorkspaceFactory.create(request=request)
    months = Reports.cumulative_budget(workspace)

    assert len(months["months"]) == 12
