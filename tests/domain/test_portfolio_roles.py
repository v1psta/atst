from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.users import Users
from atst.models.portfolio_role import Status as PortfolioRoleStatus
from atst.domain.permission_sets import PermissionSets

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
    assert len(port_role.permission_sets) == 5
    expected_names = [
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_FUNDING,
        PermissionSets.VIEW_PORTFOLIO_REPORTS,
        PermissionSets.VIEW_PORTFOLIO_ADMIN,
    ]
    actual_names = [prms.name for prms in port_role.permission_sets]
    assert expected_names == expected_names
