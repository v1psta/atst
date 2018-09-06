from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from atst.models import Base


class RequestReview(Base):
    __tablename__ = "request_reviews"

    id = Column(Integer, primary_key=True)
    status = relationship("RequestStatusEvent", back_populates="review")

    comments = Column(String)
    fname_mao = Column(String)
    lname_mao = Column(String)
    email_mao = Column(String)
    phone_mao = Column(String)
    fname_ccpo = Column(String)
    lname_ccpo = Column(String)
