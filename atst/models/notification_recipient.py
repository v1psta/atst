from sqlalchemy import String, Column

from atst.models.base import Base
import atst.models.types as types
import atst.models.mixins as mixins


class NotificationRecipient(Base, mixins.TimestampsMixin):
    __tablename__ = "notification_recipients"

    id = types.Id()
    email = Column(String, nullable=False)
