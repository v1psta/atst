from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from atst.models import Base


class RequestReview(Base):
    __tablename__ = "request_reviews"

    id = Column(BigInteger, primary_key=True)
    status = relationship("RequestStatusEvent", uselist=False, back_populates="review")

    user_id = Column(ForeignKey("users.id"), nullable=False)
    reviewer = relationship("User")

    comment = Column(String)
    fname_mao = Column(String)
    lname_mao = Column(String)
    email_mao = Column(String)
    phone_mao = Column(String)
    fname_ccpo = Column(String)
    lname_ccpo = Column(String)

    @property
    def full_name_reviewer(self):
        return self.reviewer.full_name

    @property
    def full_name_mao(self):
        return "{} {}".format(self.fname_mao, self.lname_mao)

    @property
    def full_name_ccpo(self):
        return "{} {}".format(self.fname_ccpo, self.lname_ccpo)
