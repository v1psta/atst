from enum import Enum
from sqlalchemy import Column, Date, Enum as SQLAEnum, ForeignKey, Numeric, String
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

    number = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    total_amount = Column(Numeric(scale=2), nullable=True)
    obligated_amount = Column(Numeric(scale=2), nullable=True)
    jedi_clin_type = Column(SQLAEnum(JEDICLINType, native_enum=False), nullable=True)

    #
    # NOTE: For now obligated CLINS are CLIN 1 + CLIN 3
    #
    def is_obligated(self):
        return self.jedi_clin_type in [
            JEDICLINType.JEDI_CLIN_1,
            JEDICLINType.JEDI_CLIN_3,
        ]

    @property
    def type(self):
        return "Base" if self.number[0] == "0" else "Option"

    @property
    def is_completed(self):
        return all(
            [
                self.number,
                self.start_date,
                self.end_date,
                self.total_amount,
                self.obligated_amount,
                self.jedi_clin_type,
            ]
        )

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }
