from atst.utils.context_processors import get_resources_from_context

from tests.factories import *


def test_get_resources_from_context():
    portfolio = PortfolioFactory.create()
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    assert get_resources_from_context({"portfolio_id": portfolio.id}) == (portfolio,)
    assert get_resources_from_context({"application_id": application.id}) == (
        portfolio,
        application,
    )
    assert get_resources_from_context({"environment_id": environment.id}) == (
        portfolio,
        application,
    )
    assert get_resources_from_context({"task_order_id": task_order.id}) == (
        portfolio,
        task_order,
    )
