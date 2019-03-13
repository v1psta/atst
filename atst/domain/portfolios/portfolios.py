from atst.domain.roles import Roles, PORTFOLIO_PERMISSION_SETS
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.users import Users
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.environments import Environments
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from .query import PortfoliosQuery
from .scopes import ScopedPortfolio


class PortfolioError(Exception):
    pass


class Portfolios(object):
    @classmethod
    def create(cls, user, name, defense_component=None):
        portfolio = PortfoliosQuery.create(
            name=name, defense_component=defense_component
        )
        perms_sets = [Roles.get(prms["name"]) for prms in PORTFOLIO_PERMISSION_SETS]
        Portfolios._create_portfolio_role(
            user,
            portfolio,
            status=PortfolioRoleStatus.ACTIVE,
            permission_sets=perms_sets,
        )
        PortfoliosQuery.add_and_commit(portfolio)
        return portfolio

    @classmethod
    def get(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.VIEW_PORTFOLIO, "get portfolio"
        )

        return ScopedPortfolio(user, portfolio)

    @classmethod
    def get_for_update_applications(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.CREATE_APPLICATION, "add application"
        )

        return portfolio

    @classmethod
    def get_for_update_information(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user,
            portfolio,
            Permissions.EDIT_PORTFOLIO_NAME,
            "update portfolio information",
        )

        return portfolio

    @classmethod
    def get_for_update_member(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user,
            portfolio,
            Permissions.EDIT_PORTFOLIO_USERS,
            "update a portfolio member",
        )

        return portfolio

    @classmethod
    def get_with_members(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.VIEW_PORTFOLIO_USERS, "view portfolio members"
        )

        return portfolio

    @classmethod
    def for_user(cls, user):
        if Authorization.has_atat_permission(user, Permissions.VIEW_PORTFOLIO):
            portfolios = PortfoliosQuery.get_all()
        else:
            portfolios = PortfoliosQuery.get_for_user(user)
        return portfolios

    @classmethod
    def create_member(cls, user, portfolio, data):
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.EDIT_PORTFOLIO_USERS, "create portfolio member"
        )

        new_user = Users.get_or_create_by_dod_id(
            data["dod_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            atat_role_name="default",
            provisional=True,
        )
        permission_sets = data.get("permission_sets", [])
        return Portfolios.add_member(
            portfolio, new_user, permission_sets=permission_sets
        )

    @classmethod
    def add_member(cls, portfolio, member, permission_sets=None):
        portfolio_role = PortfolioRoles.add(member, portfolio.id, permission_sets)
        return portfolio_role

    @classmethod
    def update_member(cls, user, portfolio, member, permission_sets):
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.EDIT_PORTFOLIO_USERS, "edit portfolio member"
        )

        # need to update perms sets here
        return PortfolioRoles.update(member, permission_sets)

    @classmethod
    def _create_portfolio_role(
        cls, user, portfolio, status=PortfolioRoleStatus.PENDING, permission_sets=None
    ):
        if permission_sets is None:
            permission_sets = []

        portfolio_role = PortfoliosQuery.create_portfolio_role(
            user, portfolio, status=status, permission_sets=permission_sets
        )
        PortfoliosQuery.add_and_commit(portfolio_role)
        return portfolio_role

    @classmethod
    def update(cls, portfolio, new_data):
        if "name" in new_data:
            portfolio.name = new_data["name"]

        PortfoliosQuery.add_and_commit(portfolio)

    @classmethod
    def can_revoke_access_for(cls, portfolio, portfolio_role):
        return (
            portfolio_role.user != portfolio.owner
            and portfolio_role.status == PortfolioRoleStatus.ACTIVE
        )

    @classmethod
    def revoke_access(cls, user, portfolio_id, portfolio_role_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        Authorization.check_portfolio_permission(
            user, portfolio, Permissions.EDIT_PORTFOLIO_USERS, "revoke portfolio access"
        )
        portfolio_role = PortfolioRoles.get_by_id(portfolio_role_id)

        if not Portfolios.can_revoke_access_for(portfolio, portfolio_role):
            raise PortfolioError("cannot revoke portfolio access for this user")

        portfolio_role.status = PortfolioRoleStatus.DISABLED
        for environment in portfolio.all_environments:
            Environments.revoke_access(user, environment, portfolio_role.user)
        PortfoliosQuery.add_and_commit(portfolio_role)

        return portfolio_role
