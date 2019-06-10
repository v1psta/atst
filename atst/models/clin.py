from enum import Enum
from sqlalchemy import Column, Date, Enum as SQLAEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from atst.models import Base, mixins, types


class JEDICLINType(Enum):
    JEDI_CLIN_1 = "JEDI_CLIN_1"
    JEDI_CLIN_2 = "JEDI_CLIN_2"
    JEDI_CLIN_3 = "JEDI_CLIN_3"
    JEDI_CLIN_4 = "JEDI_CLIN_4"


class CLIN(Base, mixins.TimestampsMixin):
    __tablename__ = "clins"

    id = types.Id()

    task_order_id = Column(ForeignKey("task_orders.id"), nullable=False)
    task_order = relationship("TaskOrder")

    number = Column(String, nullable=False)
    loas = Column(ARRAY(String), server_default="{}", nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    obligated_amount = Column(Numeric(scale=2), nullable=False)
    jedi_clin_type = Column(SQLAEnum(JEDICLINType, native_enum=False), nullable=False)

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }
