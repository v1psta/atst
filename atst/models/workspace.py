from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models.mixins import TimestampsMixin
from atst.utils import first_or_none
from atst.models.workspace_user import WorkspaceUser


MOCK_MEMBERS = [
    {
        "first_name": "Danny",
        "last_name": "Knight",
        "email": "dknight@thenavy.mil",
        "dod_id": "1257892124",
        "workspace_role": "Developer",
        "status": "Pending",
        "num_projects": "4",
    },
    {
        "first_name": "Mario",
        "last_name": "Hudson",
        "email": "mhudson@thearmy.mil",
        "dod_id": "4357892125",
        "workspace_role": "CCPO",
        "status": "Active",
        "num_projects": "0",
    },
    {
        "first_name": "Louise",
        "last_name": "Greer",
        "email": "lgreer@theairforce.mil",
        "dod_id": "7257892125",
        "workspace_role": "Admin",
        "status": "Pending",
        "num_projects": "43",
    },
]


class Workspace(Base, TimestampsMixin):
    __tablename__ = "workspaces"

    id = Id()
    name = Column(String, unique=True)
    request_id = Column(ForeignKey("requests.id"), nullable=False)
    projects = relationship("Project", back_populates="workspace")
    roles = relationship("WorkspaceRole")

    @property
    def owner(self):
        def _is_workspace_owner(workspace_role):
            return workspace_role.role.name == "owner"

        return first_or_none(_is_workspace_owner, self.roles)

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.users)

    @property
    def task_order(self):
        return {"number": "task-order-number"}

    @property
    def members(self):
        return [ WorkspaceUser(role.user, role) for role in self.roles]
