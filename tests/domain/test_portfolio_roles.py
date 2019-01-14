from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.users import Users
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from atst.domain.roles import Roles

from tests.factories import (
    PortfolioFactory,
    UserFactory,
    InvitationFactory,
    PortfolioRoleFactory,
)


def test_can_create_new_portfolio_role():
    portfolio = PortfolioFactory.create()
    new_user = UserFactory.create()

    portfolio_role_dicts = [{"id": new_user.id, "portfolio_role": "owner"}]
    portfolio_roles = PortfolioRoles.add_many(portfolio.id, portfolio_role_dicts)

    assert portfolio_roles[0].user_id == new_user.id
    assert portfolio_roles[0].user.atat_role.name == new_user.atat_role.name
    assert portfolio_roles[0].role.name == new_user.portfolio_roles[0].role.name


def test_can_update_existing_portfolio_role():
    portfolio = PortfolioFactory.create()
    new_user = UserFactory.create()

    PortfolioRoles.add_many(
        portfolio.id, [{"id": new_user.id, "portfolio_role": "owner"}]
    )
    portfolio_roles = PortfolioRoles.add_many(
        portfolio.id, [{"id": new_user.id, "portfolio_role": "developer"}]
    )

    assert portfolio_roles[0].user.atat_role.name == new_user.atat_role.name
    assert portfolio_roles[0].role.name == new_user.portfolio_roles[0].role.name


def test_portfolio_role_permissions():
    portfolio_one = PortfolioFactory.create()
    portfolio_two = PortfolioFactory.create()
    new_user = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio_one,
        user=new_user,
        role=Roles.get("developer"),
        status=PortfolioRoleStatus.ACTIVE,
    )
    PortfolioRoleFactory.create(
        portfolio=portfolio_two,
        user=new_user,
        role=Roles.get("developer"),
        status=PortfolioRoleStatus.PENDING,
    )

    default_perms = set(new_user.atat_role.permissions)
    assert len(
        PortfolioRoles.portfolio_role_permissions(portfolio_one, new_user)
    ) > len(default_perms)
    assert (
        PortfolioRoles.portfolio_role_permissions(portfolio_two, new_user)
        == default_perms
    )
