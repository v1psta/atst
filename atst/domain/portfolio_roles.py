from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.portfolio_role import (
    PortfolioRole,
    Status as PortfolioRoleStatus,
    MEMBER_STATUSES,
)
from atst.models.user import User

from .roles import Roles
from .users import Users
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
    def portfolio_role_permissions(cls, portfolio, user):
        portfolio_role = PortfolioRoles._get_active_portfolio_role(
            portfolio.id, user.id
        )
        atat_permissions = set(user.atat_role.permissions)
        portfolio_permissions = (
            [] if portfolio_role is None else portfolio_role.role.permissions
        )
        return set(portfolio_permissions).union(atat_permissions)

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
    def add(cls, user, portfolio_id, role_name, permission_sets=None):
        role = Roles.get(role_name)

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
            new_portfolio_role.role = role
        except NoResultFound:
            new_portfolio_role = PortfolioRole(
                user=user,
                role_id=role.id,
                portfolio_id=portfolio_id,
                status=PortfolioRoleStatus.PENDING,
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
        "view_portfolio_application_management",
        "view_portfolio_funding",
        "view_portfolio_reports",
        "view_portfolio_admin",
    }

    @classmethod
    def _permission_sets_for_names(cls, set_names):
        perms_set_names = PortfolioRoles._DEFAULT_PORTFOLIO_PERMS_SETS.union(
            set(set_names)
        )
        return [Roles.get(perms_set_name) for perms_set_name in perms_set_names]

    @classmethod
    def update_role(cls, portfolio_role, role_name):
        new_role = Roles.get(role_name)
        portfolio_role.role = new_role

        db.session.add(portfolio_role)
        db.session.commit()
        return portfolio_role

    @classmethod
    def add_many(cls, portfolio_id, portfolio_role_dicts):
        portfolio_roles = []

        for user_dict in portfolio_role_dicts:
            try:
                user = Users.get(user_dict["id"])
            except NoResultFound:
                default_role = Roles.get("developer")
                user = User(id=user_dict["id"], atat_role=default_role)

            try:
                role = Roles.get(user_dict["portfolio_role"])
            except NoResultFound:
                raise NotFoundError("role")

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
                new_portfolio_role.role = role
            except NoResultFound:
                new_portfolio_role = PortfolioRole(
                    user=user, role_id=role.id, portfolio_id=portfolio_id
                )

            user.portfolio_roles.append(new_portfolio_role)
            portfolio_roles.append(new_portfolio_role)

            db.session.add(user)

        db.session.commit()

        return portfolio_roles

    @classmethod
    def enable(cls, portfolio_role):
        portfolio_role.status = PortfolioRoleStatus.ACTIVE

        db.session.add(portfolio_role)
        db.session.commit()
