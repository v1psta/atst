from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins


class Application(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "projects"

    id = Id()
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    workspace_id = Column(ForeignKey("workspaces.id"), nullable=False)
    workspace = relationship("Workspace")
    environments = relationship("Environment", back_populates="application")

    @property
    def displayname(self):
        return self.name

    def __repr__(self):  # pragma: no cover
        return "<Application(name='{}', description='{}', workspace='{}', id='{}')>".format(
            self.name, self.description, self.workspace.name, self.id
        )
