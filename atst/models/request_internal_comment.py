from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from atst.models import Base


class RequestInternalComment(Base):
    __tablename__ = "request_internal_comments"

    id = Column(BigInteger, primary_key=True)
    text = Column(String())

    user_id = Column(ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    request_id = Column(ForeignKey("requests.id", ondelete="CASCADE"))
