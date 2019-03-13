from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, Enum as SQLAEnum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, mixins
from .types import Id

from atst.database import db
from atst.models.environment_role import EnvironmentRole
from atst.models.application import Application
from atst.models.environment import Environment


MEMBER_STATUSES = {
    "active": "Active",
    "revoked": "Invite revoked",
    "expired": "Invite expired",
    "error": "Error on invite",
    "pending": "Pending",
    "unknown": "Unknown errors",
    "disabled": "Disabled",
}


class Status(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"


portfolio_roles_roles = Table(
    "portfolio_roles_roles",
    Base.metadata,
    Column("portfolio_role_id", UUID(as_uuid=True), ForeignKey("portfolio_roles.id")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id")),
)


class PortfolioRole(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "portfolio_roles"

    id = Id()
    portfolio_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolios.id"), index=True, nullable=False
    )
    portfolio = relationship("Portfolio", back_populates="roles")

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )

    status = Column(SQLAEnum(Status, native_enum=False), default=Status.PENDING)

    permission_sets = relationship("Role", secondary=portfolio_roles_roles)

    @property
    def permissions(self):
        return [
            perm for permset in self.permission_sets for perm in permset.permissions
        ]

    def __repr__(self):
        return "<PortfolioRole(portfolio='{}', user_id='{}', id='{}', permissions={})>".format(
            self.portfolio.name, self.user_id, self.id, self.permissions
        )

    @property
    def history(self):
        previous_state = self.get_changes()
        change_set = {}
        # TODO: need to update to include permission_sets
        if "status" in previous_state:
            from_status = previous_state["status"][0].value
            to_status = self.status.value
            change_set["status"] = [from_status, to_status]
        return change_set

    @property
    def event_details(self):
        return {
            "updated_user_name": self.user_name,
            "updated_user_id": str(self.user_id),
        }

    @property
    def latest_invitation(self):
        if self.invitations:
            return self.invitations[-1]

    @property
    def display_status(self):
        if self.status == Status.ACTIVE:
            return MEMBER_STATUSES["active"]
        elif self.status == Status.DISABLED:
            return MEMBER_STATUSES["disabled"]
        elif self.latest_invitation:
            if self.latest_invitation.is_revoked:
                return MEMBER_STATUSES["revoked"]
            elif self.latest_invitation.is_rejected_wrong_user:
                return MEMBER_STATUSES["error"]
            elif (
                self.latest_invitation.is_rejected_expired
                or self.latest_invitation.is_expired
            ):
                return MEMBER_STATUSES["expired"]
            else:
                return MEMBER_STATUSES["pending"]
        else:
            return MEMBER_STATUSES["unknown"]

    @property
    def has_dod_id_error(self):
        return self.latest_invitation and self.latest_invitation.is_rejected_wrong_user

    @property
    def user_name(self):
        return self.user.full_name

    @property
    def role_displayname(self):
        return self.role.display_name

    @property
    def is_active(self):
        return self.status == Status.ACTIVE

    @property
    def num_environment_roles(self):
        return (
            db.session.query(EnvironmentRole)
            .join(EnvironmentRole.environment)
            .join(Environment.application)
            .join(Application.portfolio)
            .filter(Application.portfolio_id == self.portfolio_id)
            .filter(EnvironmentRole.user_id == self.user_id)
            .count()
        )

    @property
    def environment_roles(self):
        return (
            db.session.query(EnvironmentRole)
            .join(EnvironmentRole.environment)
            .join(Environment.application)
            .join(Application.portfolio)
            .filter(Application.portfolio_id == self.portfolio_id)
            .filter(EnvironmentRole.user_id == self.user_id)
            .all()
        )

    @property
    def has_environment_roles(self):
        return self.num_environment_roles > 0

    @property
    def can_resend_invitation(self):
        return not self.is_active and (
            self.latest_invitation and self.latest_invitation.is_inactive
        )


Index(
    "portfolio_role_user_portfolio",
    PortfolioRole.user_id,
    PortfolioRole.portfolio_id,
    unique=True,
)
