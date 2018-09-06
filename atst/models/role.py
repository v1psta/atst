from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm.attributes import flag_modified

from atst.models import Base
from .types import Id


class Role(Base):
    __tablename__ = "roles"

    id = Id()
    name = Column(String, index=True, unique=True)
    description = Column(String)
    permissions = Column(ARRAY(String), index=True, server_default="{}")

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
