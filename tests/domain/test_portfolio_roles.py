from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.users import Users
from atst.models.permissions import Permissions
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.factories import (
    PortfolioFactory,
    UserFactory,
    InvitationFactory,
    PortfolioRoleFactory,
)


def test_add_portfolio_role_with_permission_sets():
    portfolio = PortfolioFactory.create()
    new_user = UserFactory.create()
    permission_sets = [PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT]
    port_role = PortfolioRoles.add(
        new_user, portfolio.id, permission_sets=permission_sets
    )
    assert len(port_role.permission_sets) == 6
    expected_names = [
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_FUNDING,
        PermissionSets.VIEW_PORTFOLIO_REPORTS,
        PermissionSets.VIEW_PORTFOLIO_ADMIN,
        PermissionSets.VIEW_PORTFOLIO,
    ]
    actual_names = [prms.name for prms in port_role.permission_sets]
    assert expected_names == expected_names


def test_reset_default_permission_sets():
    portfolio = PortfolioFactory.create()
    user = portfolio.owner
    portfolio_role = PortfolioRoles.get(portfolio_id=portfolio.id, user_id=user.id)

    assert Permissions.EDIT_PORTFOLIO_POC in portfolio_role.permissions

    PortfolioRoles.reset_default_permission_sets(portfolio_role=portfolio_role)

    assert Permissions.EDIT_PORTFOLIO_POC not in portfolio_role.permissions
