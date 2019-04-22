from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from atst.models import Base
from atst.models.mixins import TimestampsMixin, AuditableMixin, InvitesMixin


class PortfolioInvitation(Base, TimestampsMixin, AuditableMixin, InvitesMixin):
    __tablename__ = "invitations"

    portfolio_role_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolio_roles.id"), index=True
    )
    role = relationship(
        "PortfolioRole",
        backref=backref("invitations", order_by="PortfolioInvitation.time_created"),
    )

    @property
    def portfolio(self):
        if self.role:  # pragma: no branch
            return self.role.portfolio

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
