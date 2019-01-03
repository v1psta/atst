from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from itertools import chain

from atst.models import Base, mixins, types
from atst.models.workspace_role import WorkspaceRole, Status as WorkspaceRoleStatus
from atst.utils import first_or_none
from atst.database import db


class Workspace(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "workspaces"

    id = types.Id()
    name = Column(String)
    request_id = Column(ForeignKey("requests.id"), nullable=True)
    projects = relationship("Project", back_populates="workspace")
    roles = relationship("WorkspaceRole")

    task_orders = relationship("TaskOrder")

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
        return len(self.members)

    @property
    def legacy_task_order(self):
        return self.request.legacy_task_order if self.request else None

    @property
    def members(self):
        return (
            db.session.query(WorkspaceRole)
            .filter(WorkspaceRole.workspace_id == self.id)
            .filter(WorkspaceRole.status != WorkspaceRoleStatus.DISABLED)
            .all()
        )

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

    def _find_by_role(self, role):
        try:
            return [member for member in self.members if member.role.name == role]
        except StopIteration:
            return None

    @property
    def contracting_officer(self):
        return self._find_by_role("contracting_officer")

    @property
    def contracting_officer_representative(self):
        return self._find_by_role("contracting_officer_representative")

    @property
    def security_officer(self):
        return self._find_by_role("security_officer")
