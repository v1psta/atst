from sqlalchemy import String, Column, ForeignKey, inspect
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from atst.database import db

from atst.models import Base, types
from atst.models.mixins.timestamps import TimestampsMixin


class AuditEvent(Base, TimestampsMixin):
    __tablename__ = "audit_events"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="audit_events")

    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    workspace = relationship("Workspace", backref="audit_events")

    request_id = Column(UUID(as_uuid=True), ForeignKey("requests.id"), index=True)
    request = relationship("Request", backref="audit_events")

    changed_state = Column(JSON())
    event_details = Column(JSON())

    resource_type = Column(String(), nullable=False)
    resource_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    display_name = Column(String())
    action = Column(String(), nullable=False)


    def save(self, connection):
        attrs = inspect(self).dict

        connection.execute(self.__table__.insert(), **attrs)

    def __repr__(self):
        return "<AuditEvent(name='{}', action='{}', id='{}')>".format(
            self.display_name, self.action, self.id
        )
