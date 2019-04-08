from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, Enum as SQLAEnum, Table, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, mixins
from .types import Id

from atst.database import db
from atst.utils import first_or_none
from atst.models.environment_role import EnvironmentRole
from atst.models.application import Application
from atst.models.environment import Environment
from atst.models.mixins.auditable import ACTION_UPDATE as AUDIT_ACTION_UPDATE


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


portfolio_roles_permission_sets = Table(
    "portfolio_roles_permission_sets",
    Base.metadata,
    Column("portfolio_role_id", UUID(as_uuid=True), ForeignKey("portfolio_roles.id")),
    Column("permission_set_id", UUID(as_uuid=True), ForeignKey("permission_sets.id")),
)


class PortfolioRole(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.PermissionsMixin
):
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

    permission_sets = relationship(
        "PermissionSet", secondary=portfolio_roles_permission_sets
    )

    def __repr__(self):
        return "<PortfolioRole(portfolio='{}', user_id='{}', id='{}', permissions={})>".format(
            self.portfolio.name, self.user_id, self.id, self.permissions
        )

    @property
    def history(self):
        previous_state = self.get_changes()
        change_set = {}
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

    def has_permission_set(self, perm_set_name):
        return first_or_none(
            lambda prms: prms.name == perm_set_name, self.permission_sets
        )

    @property
    def has_dod_id_error(self):
        return self.latest_invitation and self.latest_invitation.is_rejected_wrong_user

    @property
    def user_name(self):
        return self.user.full_name

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


@event.listens_for(PortfolioRole.permission_sets, "bulk_replace", raw=True)
def record_permission_sets_updates(instance_state, permission_sets, initiator):
    old_perm_sets = instance_state.attrs.get("permission_sets").value
    if instance_state.persistent and old_perm_sets != permission_sets:
        connection = instance_state.session.connection()
        old_state = [p.name for p in old_perm_sets]
        new_state = [p.name for p in permission_sets]
        changed_state = {"permission_sets": (old_state, new_state)}
        instance_state.object.create_audit_event(
            connection,
            instance_state.object,
            AUDIT_ACTION_UPDATE,
            changed_state=changed_state,
        )
