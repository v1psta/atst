from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from itertools import chain

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins
from atst.utils import first_or_none


class Workspace(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "workspaces"

    id = Id()
    name = Column(String)
    request_id = Column(ForeignKey("requests.id"), nullable=False)
    projects = relationship("Project", back_populates="workspace")
    roles = relationship("WorkspaceRole")

    @property
    def owner(self):
        def _is_workspace_owner(workspace_role):
            return workspace_role.role.name == "owner"

        owner = first_or_none(_is_workspace_owner, self.roles)
        return owner.user if owner else None

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.users)

    @property
    def task_order(self):
        return self.request.task_order

    @property
    def members(self):
        return self.roles

    @property
    def displayname(self):
        return self.name

    @property
    def all_environments(self):
        return list(chain.from_iterable(p.environments for p in self.projects))

    def auditable_workspace_id(self):
        return self.id

    def __repr__(self):
        return "<Workspace(name='{}', request='{}', user_count='{}', id='{}')>".format(
            self.name, self.request_id, self.user_count, self.id
        )
