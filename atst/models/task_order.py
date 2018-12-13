from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class TaskOrder(Base, mixins.TimestampsMixin):
    __tablename__ = "task_orders"

    id = types.Id()
    number = Column(String, unique=True)
    clin_0001 = Column(Integer)
    clin_0003 = Column(Integer)
    clin_1001 = Column(Integer)
    clin_1003 = Column(Integer)
    clin_2001 = Column(Integer)
    clin_2003 = Column(Integer)
    expiration_date = Column(Date)

    workspace_id = Column(ForeignKey("workspaces.id"))
    workspace = relationship("Workspace")

    user_id = Column(ForeignKey("users.id"))
    creator = relationship("User")

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
        return "<TaskOrder(number='{}', budget='{}', expiration_date='{}', id='{}')>".format(
            self.number, self.budget, self.expiration_date, self.id
        )
