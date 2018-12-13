from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAEnum, Date
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class Source(Enum):
    MANUAL = "Manual"
    EDA = "EDA"


class FundingType(Enum):
    RDTE = "RDTE"
    OM = "OM"
    PROC = "PROC"
    OTHER = "OTHER"


class LegacyTaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "legacy_task_orders"

    id = types.Id()
    number = Column(String, unique=True)
    source = Column(SQLAEnum(Source, native_enum=False))
    funding_type = Column(SQLAEnum(FundingType, native_enum=False))
    funding_type_other = Column(String)
    clin_0001 = Column(Integer)
    clin_0003 = Column(Integer)
    clin_1001 = Column(Integer)
    clin_1003 = Column(Integer)
    clin_2001 = Column(Integer)
    clin_2003 = Column(Integer)
    expiration_date = Column(Date)

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

    @property
    def budget(self):
        return sum(
            filter(
                None,
                [
                    self.clin_0001,
                    self.clin_0003,
                    self.clin_1001,
                    self.clin_1003,
                    self.clin_2001,
                    self.clin_2003,
                ],
            )
        )

    def __repr__(self):
        return "<LegacyTaskOrder(number='{}', verified='{}', budget='{}', expiration_date='{}', pdf='{}', id='{}')>".format(
            self.number,
            self.verified,
            self.budget,
            self.expiration_date,
            self.pdf,
            self.id,
        )
