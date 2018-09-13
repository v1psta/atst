from sqlalchemy import String, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class AuditEvent(Base, mixins.TimestampsMixin):
    __tablename__ = "audit_events"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="audit_events")

    resource_name = Column(String())
    resource_id = Column(UUID(as_uuid=True), index=True)
    action = Column(String())

    def __str__(self):
        user_name = self.user.full_name

        if self.action == "create request":
            return "{} created request {}".format(user_name, self.resource_id)
        else:
            return "{} {} {} {}".format(
                user_name, self.action, self.resource_name, self.resource_id
            )
