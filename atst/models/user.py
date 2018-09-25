from sqlalchemy import String, ForeignKey, Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base, types, mixins
from atst.models.permissions import Permissions


class User(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "users"

    id = types.Id()
    username = Column(String)
    atat_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))

    atat_role = relationship("Role")
    workspace_roles = relationship("WorkspaceRole", backref="user")

    email = Column(String, unique=True)
    dod_id = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)

    @property
    def atat_permissions(self):
        return self.atat_role.permissions

    @property
    def atat_role_name(self):
        return self.atat_role.name

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def has_workspaces(self):
        return (
            Permissions.VIEW_WORKSPACE in self.atat_role.permissions
        ) or self.workspace_roles
