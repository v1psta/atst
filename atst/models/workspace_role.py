from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, Enum as SQLAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, mixins
from .types import Id


class Status(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"


class WorkspaceRole(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "workspace_roles"

    id = Id()
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True, nullable=False
    )
    workspace = relationship("Workspace", back_populates="roles")

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )

    status = Column(SQLAEnum(Status, native_enum=False, default=Status.PENDING))

    def __repr__(self):
        return "<WorkspaceRole(role='{}', workspace='{}', user_id='{}', id='{}')>".format(
            self.role.name, self.workspace.name, self.user_id, self.id
        )

    @property
    def display_status(self):
        if self.status == Status.ACTIVE:
            return "Active"
        else:
            if any(i.is_expired for i in self.invitations):
                return "Invitation Expired"
            elif any(i.is_rejected for i in self.invitations):
                return "Invitation Rejected"
            else:
                return "Pending"


Index(
    "workspace_role_user_workspace",
    WorkspaceRole.user_id,
    WorkspaceRole.workspace_id,
    unique=True,
)
