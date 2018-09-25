from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins


class Environment(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "environments"

    id = Id()
    name = Column(String, nullable=False)

    project_id = Column(ForeignKey("projects.id"), nullable=False)
    project = relationship("Project")

    @property
    def users(self):
        return [r.user for r in self.roles]

    @property
    def num_users(self):
        return len(self.users)

    @property
    def displayname(self):
        return self.name

    def auditable_workspace_id(self):
        return self.project.workspace_id
