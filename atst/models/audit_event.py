from sqlalchemy import String, Column, ForeignKey, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types
from atst.models.mixins.timestamps import TimestampsMixin


class AuditEvent(Base, TimestampsMixin):
    __tablename__ = "audit_events"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="audit_events")

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    workspace = relationship("Workspace", backref="audit_events")

    resource_type = Column(String(), nullable=False)
    resource_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    display_name = Column(String())
    action = Column(String(), nullable=False)

    def __str__(self):

        user_str = "{} performed".format(self.user.full_name) if self.user else "ATAT System"
        action_str = "{} on {} {}".format(
            self.action, self.resource_type, self.resource_id
        )
        display_name_str = "({})".format(self.display_name) if self.display_name else ""
        workspace_str = "in workspace {}".format(self.workspace_id) if self.workspace_id else ""

        return " ".join([user_str, action_str, display_name_str, workspace_str])

    def save(self, connection):
        attrs = inspect(self).dict

        connection.execute(self.__table__.insert(), **attrs)
