from atst.domain.environments import Environments
from atst.domain.applications import Applications
from tests.factories import PortfolioFactory, UserFactory


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = Applications.create(
        portfolio, "my test application", "It's mine.", ["dev", "staging", "prod"]
    )
    dev_environment = application.environments[0]

    dev_environment = Environments.add_member(dev_environment, developer, "developer")
    assert developer in dev_environment.users
