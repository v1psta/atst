import pytest

from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import NotFoundError

from tests.factories import *


def test_get_for_portfolio():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)
    env_role = EnvironmentRoleFactory.create(
        environment=environment, user=user, role="basic access"
    )

    assert (
        EnvironmentRoles.get_for_portfolio(
            user.id, environment.id, portfolio_id=portfolio.id
        )
        == env_role
    )
    with pytest.raises(NotFoundError):
        EnvironmentRoles.get_for_portfolio(
            user.id, environment.id, portfolio_id=application.id
        )
