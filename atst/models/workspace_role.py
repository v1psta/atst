from sqlalchemy import Index, ForeignKey, Column, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, mixins
from .types import Id


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

    accepted = Column(Boolean)

    def __repr__(self):
        return "<WorkspaceRole(role='{}', workspace='{}', user_id='{}', id='{}')>".format(
            self.role.name, self.workspace.name, self.user_id, self.id
        )


Index(
    "workspace_role_user_workspace",
    WorkspaceRole.user_id,
    WorkspaceRole.workspace_id,
    unique=True,
)
