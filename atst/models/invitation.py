from sqlalchemy import Column, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types
from atst.models.mixins.timestamps import TimestampsMixin


class Invitation(Base, TimestampsMixin):
    __tablename__ = "invitations"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="invitations")

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    workspace = relationship("Workspace", backref="invitations")

    valid = Column(Boolean, default=True)

    def __repr__(self):
        return "<Invitation(user='{}', workspace='{}', id='{}')>".format(
            self.user.id, self.workspace.id, self.id
        )
