from sqlalchemy import Index, ForeignKey, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, mixins
from .types import Id


class WorkspaceRole(Base, mixins.TimestampsMixin):
    __tablename__ = "workspace_roles"

    id = Id()
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True, nullable=False)
    workspace = relationship("Workspace", back_populates="roles")

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    role = relationship("Role")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)


Index(
    "workspace_role_user_workspace",
    WorkspaceRole.user_id,
    WorkspaceRole.workspace_id,
    unique=True,
)
