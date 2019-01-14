from atst.domain.reports import Reports

from tests.factories import RequestFactory, LegacyTaskOrderFactory, PortfolioFactory

CLIN_NUMS = ["0001", "0003", "1001", "1003", "2001", "2003"]


def test_portfolio_totals():
    legacy_task_order = LegacyTaskOrderFactory.create()

    for num in CLIN_NUMS:
        setattr(legacy_task_order, "clin_{}".format(num), 200)

    request = RequestFactory.create(legacy_task_order=legacy_task_order)
    portfolio = PortfolioFactory.create(request=request)
    report = Reports.portfolio_totals(portfolio)
    total = 200 * len(CLIN_NUMS)
    assert report == {"budget": total, "spent": 0}


# this is sketched in until we do real reporting
def test_monthly_totals():
    request = RequestFactory.create()
    portfolio = PortfolioFactory.create(request=request)
    monthly = Reports.monthly_totals(portfolio)

    assert not monthly["environments"]
    assert not monthly["applications"]
    assert not monthly["portfolio"]


# this is sketched in until we do real reporting
def test_cumulative_budget():
    request = RequestFactory.create()
    portfolio = PortfolioFactory.create(request=request)
    months = Reports.cumulative_budget(portfolio)

    assert len(months["months"]) == 12
