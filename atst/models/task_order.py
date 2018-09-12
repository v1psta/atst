from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from atst.models import Base


class Source(Enum):
    MANUAL = "Manual"
    EDA = "EDA"


class FundingType(Enum):
    RDTE = "RDTE"
    OM = "OM"
    PROC = "PROC"
    OTHER = "OTHER"


class TaskOrder(Base):
    __tablename__ = "task_order"

    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    source = Column(SQLAEnum(Source))
    funding_type = Column(SQLAEnum(FundingType))
    funding_type_other = Column(String)
    clin_0001 = Column(Integer)
    clin_0003 = Column(Integer)
    clin_1001 = Column(Integer)
    clin_1003 = Column(Integer)
    clin_2001 = Column(Integer)
    clin_2003 = Column(Integer)

    attachment_id = Column(ForeignKey("attachments.id"))
    pdf = relationship("Attachment")

    @property
    def verified(self):
        return self.source == Source.EDA

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id", "attachment_id"]
        }
