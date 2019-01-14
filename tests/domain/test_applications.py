from atst.domain.applications import Applications
from tests.factories import RequestFactory, UserFactory, PortfolioFactory
from atst.domain.portfolios import Portfolios


def test_create_application_with_multiple_environments():
    request = RequestFactory.create()
    portfolio = Portfolios.create_from_request(request)
    application = Applications.create(
        portfolio.owner, portfolio, "My Test Application", "Test", ["dev", "prod"]
    )

    assert application.portfolio == portfolio
    assert application.name == "My Test Application"
    assert application.description == "Test"
    assert sorted(e.name for e in application.environments) == ["dev", "prod"]


def test_portfolio_owner_can_view_environments():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"environments": [{"name": "dev"}, {"name": "prod"}]}],
    )
    application = Applications.get(owner, portfolio, portfolio.applications[0].id)

    assert len(application.environments) == 2


def test_can_only_update_name_and_description():
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[
            {
                "name": "Application 1",
                "description": "a application",
                "environments": [{"name": "dev"}],
            }
        ],
    )
    application = Applications.get(owner, portfolio, portfolio.applications[0].id)
    env_name = application.environments[0].name
    Applications.update(
        owner,
        portfolio,
        application,
        {
            "name": "New Name",
            "description": "a new application",
            "environment_name": "prod",
        },
    )

    assert application.name == "New Name"
    assert application.description == "a new application"
    assert len(application.environments) == 1
    assert application.environments[0].name == env_name
