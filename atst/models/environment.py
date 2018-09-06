from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models.mixins import TimestampsMixin


class Environment(Base, TimestampsMixin):
    __tablename__ = "environments"

    id = Id()
    name = Column(String, nullable=False)

    project_id = Column(ForeignKey("projects.id"))
    project = relationship("Project")

    @property
    def users(self):
        return [r.user for r in self.roles]
