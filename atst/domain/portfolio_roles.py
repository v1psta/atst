from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.portfolio_role import (
    PortfolioRole,
    Status as PortfolioRoleStatus,
    MEMBER_STATUSES,
)
from atst.models.user import User

from .permission_sets import PermissionSets
from .exceptions import NotFoundError


MEMBER_STATUS_CHOICES = [
    dict(name=key, display_name=value) for key, value in MEMBER_STATUSES.items()
]


class PortfolioRoles(object):
    @classmethod
    def get(cls, portfolio_id, user_id):
        try:
            portfolio_role = (
                db.session.query(PortfolioRole)
                .join(User)
                .filter(User.id == user_id, PortfolioRole.portfolio_id == portfolio_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("portfolio_role")

        return portfolio_role

    @classmethod
    def get_by_id(cls, id_):
        try:
            return db.session.query(PortfolioRole).filter(PortfolioRole.id == id_).one()
        except NoResultFound:
            raise NotFoundError("portfolio_role")

    @classmethod
    def _get_active_portfolio_role(cls, portfolio_id, user_id):
        try:
            return (
                db.session.query(PortfolioRole)
                .join(User)
                .filter(User.id == user_id, PortfolioRole.portfolio_id == portfolio_id)
                .filter(PortfolioRole.status == PortfolioRoleStatus.ACTIVE)
                .one()
            )
        except NoResultFound:
            return None

    @classmethod
    def _get_portfolio_role(cls, user, portfolio_id):
        try:
            existing_portfolio_role = (
                db.session.query(PortfolioRole)
                .filter(
                    PortfolioRole.user == user,
                    PortfolioRole.portfolio_id == portfolio_id,
                )
                .one()
            )
            return existing_portfolio_role
        except NoResultFound:
            raise NotFoundError("portfolio role")

    @classmethod
    def add(cls, user, portfolio_id, permission_sets=None):
        new_portfolio_role = None
        try:
            existing_portfolio_role = (
                db.session.query(PortfolioRole)
                .filter(
                    PortfolioRole.user == user,
                    PortfolioRole.portfolio_id == portfolio_id,
                )
                .one()
            )
            new_portfolio_role = existing_portfolio_role
        except NoResultFound:
            new_portfolio_role = PortfolioRole(
                user=user, portfolio_id=portfolio_id, status=PortfolioRoleStatus.PENDING
            )

        if permission_sets:
            new_portfolio_role.permission_sets = PortfolioRoles._permission_sets_for_names(
                permission_sets
            )

        user.portfolio_roles.append(new_portfolio_role)
        db.session.add(user)
        db.session.commit()

        return new_portfolio_role

    _DEFAULT_PORTFOLIO_PERMS_SETS = {
        PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT,
        PermissionSets.VIEW_PORTFOLIO_FUNDING,
        PermissionSets.VIEW_PORTFOLIO_REPORTS,
        PermissionSets.VIEW_PORTFOLIO_ADMIN,
    }

    @classmethod
    def _permission_sets_for_names(cls, set_names):
        perms_set_names = PortfolioRoles._DEFAULT_PORTFOLIO_PERMS_SETS.union(
            set(set_names)
        )
        return [
            PermissionSets.get(perms_set_name) for perms_set_name in perms_set_names
        ]

    @classmethod
    def update(cls, portfolio_role, set_names):
        new_permission_sets = PortfolioRoles._permission_sets_for_names(set_names)
        portfolio_role.permission_sets = new_permission_sets

        db.session.add(portfolio_role)
        db.session.commit()

        return portfolio_role

    @classmethod
    def enable(cls, portfolio_role):
        portfolio_role.status = PortfolioRoleStatus.ACTIVE

        db.session.add(portfolio_role)
        db.session.commit()
