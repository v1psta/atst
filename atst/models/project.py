from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models.mixins import TimestampsMixin


class Project(Base, TimestampsMixin):
    __tablename__ = "projects"

    id = Id()
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    workspace_id = Column(ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace")
    environments = relationship("Environment", back_populates="project")
