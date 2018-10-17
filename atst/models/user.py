from sqlalchemy import String, ForeignKey, Column, Date
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
    phone_number = Column(String)
    service_branch = Column(String)
    citizenship = Column(String)
    designation = Column(String)
    date_latest_training = Column(Date)

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

    @property
    def displayname(self):
        return self.full_name

    def __repr__(self):
        return "<User(name='{}', dod_id='{}', email='{}', role='{}', has_workspaces='{}', id='{}')>".format(
            self.full_name,
            self.dod_id,
            self.email,
            self.atat_role_name,
            self.has_workspaces,
            self.id,
        )

    def to_dictionary(self):
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in ["id"]
        }
