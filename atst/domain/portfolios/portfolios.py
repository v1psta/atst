from atst.database import db
from atst.domain.permission_sets import PermissionSets
from atst.domain.authz import Authorization
from atst.domain.portfolio_roles import PortfolioRoles
from atst.domain.invitations import PortfolioInvitations
from atst.domain.environments import Environments
from atst.models import Permissions, PortfolioRole, PortfolioRoleStatus

from .query import PortfoliosQuery
from .scopes import ScopedPortfolio


class PortfolioError(Exception):
    pass


class PortfolioDeletionApplicationsExistError(Exception):
    pass


class Portfolios(object):
    @classmethod
    def create(cls, user, portfolio_attrs):
        portfolio = PortfoliosQuery.create(**portfolio_attrs)
        perms_sets = PermissionSets.get_many(PortfolioRoles.PORTFOLIO_PERMISSION_SETS)
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
        return ScopedPortfolio(user, portfolio)

    @classmethod
    def delete(cls, portfolio):
        if len(portfolio.applications) != 0:
            raise PortfolioDeletionApplicationsExistError()

        for portfolio_role in portfolio.roles:
            PortfolioRoles.disable(portfolio_role)

        portfolio.deleted = True

        db.session.add(portfolio)
        db.session.commit()

        return portfolio

    @classmethod
    def get_for_update(cls, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)

        return portfolio

    @classmethod
    def for_user(cls, user):
        if Authorization.has_atat_permission(user, Permissions.VIEW_PORTFOLIO):
            portfolios = PortfoliosQuery.get_all()
        else:
            portfolios = PortfoliosQuery.get_for_user(user)
        return portfolios

    @classmethod
    def add_member(cls, portfolio, member, permission_sets=None):
        portfolio_role = PortfolioRoles.add(member, portfolio.id, permission_sets)
        return portfolio_role

    @classmethod
    def invite(cls, portfolio, inviter, member_data):
        permission_sets = PortfolioRoles._permission_sets_for_names(
            member_data.get("permission_sets", [])
        )
        role = PortfolioRole(portfolio_id=portfolio.id, permission_sets=permission_sets)

        invitation = PortfolioInvitations.create(
            inviter=inviter, role=role, member_data=member_data
        )

        PortfoliosQuery.add_and_commit(role)

        return invitation

    @classmethod
    def update_member(cls, member, permission_sets):
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
    def revoke_access(cls, portfolio_id, portfolio_role_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        portfolio_role = PortfolioRoles.get_by_id(portfolio_role_id)

        if not Portfolios.can_revoke_access_for(portfolio, portfolio_role):
            raise PortfolioError("cannot revoke portfolio access for this user")

        portfolio_role.status = PortfolioRoleStatus.DISABLED
        for environment in portfolio.all_environments:
            Environments.revoke_access(environment, portfolio_role.user)
        PortfoliosQuery.add_and_commit(portfolio_role)

        return portfolio_role
