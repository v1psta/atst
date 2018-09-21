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

    resource_name = Column(String(), nullable=False)
    resource_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    action = Column(String(), nullable=False)

    def __str__(self):
        full_action = "{} on {} {}".format(
            self.action, self.resource_name, self.resource_id
        )

        if self.user and self.workspace:
            return "{} performed {} in workspace {}".format(
                self.user.full_name, full_action, self.workspace_id
            )
        if self.user:
            return "{} performed {}".format(self.user.full_name, full_action)
        else:
            return "ATAT System performed {}".format(full_action)

    def save(self, connection):
        attrs = inspect(self).dict

        connection.execute(self.__table__.insert(), **attrs)
