from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm.attributes import flag_modified

from atst.models import Base, types, mixins


class Role(Base, mixins.TimestampsMixin):
    __tablename__ = "roles"

    id = types.Id()
    name = Column(String, index=True, unique=True, nullable=False)
    description = Column(String, nullable=False)
    permissions = Column(ARRAY(String), index=True, server_default="{}", nullable=False)

    def add_permission(self, permission):
        perms_set = set(self.permissions)
        perms_set.add(permission)
        self.permissions = list(perms_set)
        flag_modified(self, "permissions")

    def remove_permission(self, permission):
        perms_set = set(self.permissions)
        perms_set.discard(permission)
        self.permissions = list(perms_set)
        flag_modified(self, "permissions")
