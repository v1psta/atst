from sqlalchemy import Column, ForeignKey, String, func
from sqlalchemy.orm import relationship

from atst.database import db
from atst.models import Base
from atst.models.workspace_role import WorkspaceRole
from atst.models.types import Id
from atst.models.mixins import TimestampsMixin


class Workspace(Base, TimestampsMixin):
    __tablename__ = "workspaces"

    id = Id()
    name = Column(String, unique=True)

    request_id = Column(ForeignKey("requests.id"), nullable=False)
    request = relationship("Request")
    projects = relationship("Project", back_populates="workspace")

    @property
    def owner(self):
        return self.request.creator

    @property
    def task_order(self):
        return {"number": 123}

    @property
    def user_count(self):
        return db.session.query(
            func.count(WorkspaceRole.id).filter(WorkspaceRole.workspace == self)
        ).scalar()
