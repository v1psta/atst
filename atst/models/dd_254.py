from sqlalchemy import Column, String
from sqlalchemy.types import ARRAY
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class DD254(Base, mixins.TimestampsMixin):
    __tablename__ = "dd_254s"

    id = types.Id()

    certifying_official = Column(String)
    co_title = Column(String)
    co_address = Column(String)
    co_phone = Column(String)
    required_distribution = Column(ARRAY(String))

    task_order = relationship("TaskOrder", uselist=False, backref="task_order")

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }

    def __repr__(self):
        return "<DD254(certifying_official='{}', task_order='{}', id='{}')>".format(
            self.certifying_official, self.task_order.id, self.id
        )
