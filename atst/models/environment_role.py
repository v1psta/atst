from enum import Enum
from sqlalchemy import Index, ForeignKey, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base, types, mixins


class CSPRole(Enum):
    NONSENSE_ROLE = "nonsense_role"


class EnvironmentRole(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "environment_roles"

    id = types.Id()
    environment_id = Column(
        UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False
    )
    environment = relationship("Environment", backref="roles")

    role = Column(String())

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="environment_roles")

    def __repr__(self):
        return "<EnvironmentRole(role='{}', user='{}', environment='{}', id='{}')>".format(
            self.role, self.user.full_name, self.environment.name, self.id
        )

    @property
    def history(self):
        previous_state = mixins.AuditableMixin.get_history(self)
        auditable_previous_state = {}
        if "role" in previous_state:
            from_role = previous_state["role"]
            to_role = self.role
            auditable_previous_state["role"] = [from_role, to_role]
        return auditable_previous_state

    @property
    def event_details(self):
        return {
            "updated_user": self.user.displayname,
            "updated_user_id": str(self.user_id),
            "environment": self.environment.displayname,
            "environment_id": str(self.environment_id),
            "project": self.environment.project.name,
            "project_id": str(self.environment.project_id),
            "workspace": self.environment.project.workspace.name,
            "workspace_id": str(self.environment.project.workspace.id),
        }


Index(
    "environments_role_user_environment",
    EnvironmentRole.user_id,
    EnvironmentRole.environment_id,
    unique=True,
)
