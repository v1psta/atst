from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class CSPRole(Enum):
    NONSENSE_ROLE = "nonesense_role"


class EnvironmentRole(Base, mixins.TimestampsMixin):
    __tablename__ = "environment_roles"

    id = types.Id()
    environment_id = Column(UUID(as_uuid=True), ForeignKey("environments.id"))
    environment = relationship("Environment", backref="roles")

    role = Column(String())

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", backref="environment_roles")


Index(
    "environments_role_user_environment",
    EnvironmentRole.user_id,
    EnvironmentRole.environment_id,
    unique=True,
)
