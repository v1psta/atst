from atst.domain.environments import Environments
from atst.domain.portfolios import Portfolios
from atst.domain.applications import Applications
from tests.factories import RequestFactory, UserFactory


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.from_atat_role("developer")

    portfolio = Portfolios.create_from_request(RequestFactory.create(creator=owner))
    application = Applications.create(
        owner,
        portfolio,
        "my test application",
        "It's mine.",
        ["dev", "staging", "prod"],
    )
    dev_environment = application.environments[0]

    dev_environment = Environments.add_member(dev_environment, developer, "developer")
    assert developer in dev_environment.users
