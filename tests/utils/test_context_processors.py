import pytest

from atst.domain.permission_sets import PermissionSets
from atst.models import Permissions
from atst.utils.context_processors import get_resources_from_context, user_can_view

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


@pytest.fixture
def set_g(request_ctx):
    def _set_g(attr, val):
        setattr(request_ctx.g, attr, val)

    yield _set_g

    setattr(request_ctx.g, "application", None)
    setattr(request_ctx.g, "portfolio", None)
    setattr(request_ctx.g, "current_user", None)


def test_user_can_view(set_g):
    owner = UserFactory.create()
    app_user = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        user=app_user,
        application=application,
        permission_sets=PermissionSets.get_many([PermissionSets.VIEW_APPLICATION]),
    )

    set_g("portfolio", portfolio)
    set_g("application", application)
    set_g("current_user", owner)
    assert user_can_view(Permissions.VIEW_APPLICATION)

    set_g("current_user", app_user)
    assert user_can_view(Permissions.VIEW_APPLICATION)

    set_g("current_user", rando)
    assert not user_can_view(Permissions.VIEW_APPLICATION)
