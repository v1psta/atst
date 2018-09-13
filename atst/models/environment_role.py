from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins
from atst.database import db
from .types import Id


class CSPRole(Enum):
    NONSENSE_ROLE = "nonsense_role"


class EnvironmentRole(Base, mixins.TimestampsMixin):
    __tablename__ = "environment_roles"

    id = types.Id()
    environment_id = Column(
        UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False
    )
    environment = relationship("Environment", backref="roles")

    role = Column(String())

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="environment_roles")

    @classmethod
    def get(cls, user_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .filter(
                EnvironmentRole.user_id == user_id,
                EnvironmentRole.environment_id == environment_id,
            )
            .one_or_none()
        )
        return existing_env_role


Index(
    "environments_role_user_environment",
    EnvironmentRole.user_id,
    EnvironmentRole.environment_id,
    unique=True,
)
