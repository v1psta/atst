from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from atst.models import Base
from atst.models.mixins import TimestampsMixin, AuditableMixin, InvitesMixin


class ApplicationInvitation(Base, TimestampsMixin, AuditableMixin, InvitesMixin):
    __tablename__ = "application_invitations"

    application_role_id = Column(
        UUID(as_uuid=True), ForeignKey("application_roles.id"), index=True
    )
    role = relationship(
        "ApplicationRole",
        backref=backref("invitations", order_by="ApplicationInvitation.time_created"),
    )

    @property
    def application(self):
        if self.role:  # pragma: no branch
            return self.role.application

    @property
    def application_id(self):
        return self.role.application_id

    @property
    def portfolio_id(self):
        return self.role.portfolio_id

    @property
    def event_details(self):
        return {"email": self.email, "dod_id": self.user_dod_id}

    @property
    def history(self):
        changes = self.get_changes()
        change_set = {}

        if "status" in changes:
            change_set["status"] = [s.name for s in changes["status"]]

        return change_set
