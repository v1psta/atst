from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Id()

    request_id = Column(ForeignKey("requests.id"), nullable=False)
    request = relationship("Request")

    name = Column(String, unique=True)

    @property
    def owner(self):
        return self.request.creator
