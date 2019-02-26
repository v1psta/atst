from atst.domain.reports import Reports

from tests.factories import PortfolioFactory


def test_portfolio_totals():
    portfolio = PortfolioFactory.create()
    report = Reports.portfolio_totals(portfolio)
    assert report == {"budget": 0, "spent": 0}


# this is sketched in until we do real reporting
def test_monthly_totals():
    portfolio = PortfolioFactory.create()
    monthly = Reports.monthly_totals(portfolio)

    assert not monthly["environments"]
    assert not monthly["applications"]
    assert not monthly["portfolio"]


# this is sketched in until we do real reporting
def test_cumulative_budget():
    portfolio = PortfolioFactory.create()
    months = Reports.cumulative_budget(portfolio)

    assert len(months["months"]) >= 12
