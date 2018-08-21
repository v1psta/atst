from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models.mixins import TimestampsMixin


class Workspace(Base, TimestampsMixin):
    __tablename__ = "workspaces"

    id = Id()
    name = Column(String, unique=True)
    request_id = Column(ForeignKey("requests.id"), nullable=False)
    request = relationship("Request")
    projects = relationship("Project", back_populates="workspace")
    roles = relationship("WorkspaceRole")

    @property
    def owner(self):
        return self.request.creator

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.users)

    @property
    def task_order(self):
        return {"number": "task-order-number"}
