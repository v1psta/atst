from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, Enum as SQLAEnum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.event import listen

from atst.utils import first_or_none
from atst.models import Base, mixins
from atst.models.mixins.auditable import record_permission_sets_updates
from .types import Id


class Status(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"


application_roles_permission_sets = Table(
    "application_roles_permission_sets",
    Base.metadata,
    Column(
        "application_role_id", UUID(as_uuid=True), ForeignKey("application_roles.id")
    ),
    Column("permission_set_id", UUID(as_uuid=True), ForeignKey("permission_sets.id")),
)


class ApplicationRole(
    Base,
    mixins.TimestampsMixin,
    mixins.AuditableMixin,
    mixins.PermissionsMixin,
    mixins.DeletableMixin,
):
    __tablename__ = "application_roles"

    id = Id()
    application_id = Column(
        UUID(as_uuid=True), ForeignKey("applications.id"), index=True, nullable=False
    )
    application = relationship("Application", back_populates="roles")

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )

    status = Column(SQLAEnum(Status, native_enum=False), default=Status.PENDING)

    permission_sets = relationship(
        "PermissionSet", secondary=application_roles_permission_sets
    )

    @property
    def user_name(self):
        return self.user.full_name

    def __repr__(self):
        return "<ApplicationRole(application='{}', user_id='{}', id='{}', permissions={})>".format(
            self.application.name, self.user_id, self.id, self.permissions
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

    def has_permission_set(self, perm_set_name):
        return first_or_none(
            lambda prms: prms.name == perm_set_name, self.permission_sets
        )

    @property
    def portfolio_id(self):
        return self.application.portfolio_id

Index(
    "application_role_user_application",
    ApplicationRole.user_id,
    ApplicationRole.application_id,
    unique=True,
)


listen(
    ApplicationRole.permission_sets,
    "bulk_replace",
    record_permission_sets_updates,
    raw=True,
)
