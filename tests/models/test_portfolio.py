from tests.factories import ApplicationFactory, PortfolioFactory


def test_portfolio_applications_excludes_deleted():
    portfolio = PortfolioFactory.create()
    app = ApplicationFactory.create(portfolio=portfolio)
    ApplicationFactory.create(portfolio=portfolio, deleted=True)
    assert len(portfolio.applications) == 1
    assert portfolio.applications[0].id == app.id
