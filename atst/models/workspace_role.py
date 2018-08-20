from sqlalchemy import Index, ForeignKey, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base
from .types import Id


class WorkspaceRole(Base):
    __tablename__ = "workspace_role"

    id = Id()
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    workspace = relationship("Workspace")

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    role = relationship("Role")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)


Index(
    "workspace_role_user_workspace",
    WorkspaceRole.user_id,
    WorkspaceRole.workspace_id,
    unique=True,
)
