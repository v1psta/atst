from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class RequestInternalComment(Base, mixins.TimestampsMixin):
    __tablename__ = "request_internal_comments"

    id = types.Id()
    text = Column(String())

    user_id = Column(ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    request_id = Column(ForeignKey("requests.id", ondelete="CASCADE"))
