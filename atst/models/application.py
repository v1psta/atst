from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins

from atst.models.application_role import (
    ApplicationRole,
    Status as ApplicationRoleStatuses,
)
from atst.database import db


class Application(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    __tablename__ = "applications"

    id = Id()
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    portfolio_id = Column(ForeignKey("portfolios.id"), nullable=False)
    portfolio = relationship("Portfolio")
    environments = relationship(
        "Environment",
        back_populates="application",
        primaryjoin="and_(Environment.application_id==Application.id, Environment.deleted==False)",
    )
    roles = relationship("ApplicationRole")

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def members(self):
        return (
            db.session.query(ApplicationRole)
            .filter(ApplicationRole.application_id == self.id)
            .filter(ApplicationRole.status != ApplicationRoleStatuses.DISABLED)
            .all()
        )

    @property
    def num_users(self):
        return len(self.users)

    @property
    def displayname(self):
        return self.name

    def __repr__(self):  # pragma: no cover
        return "<Application(name='{}', description='{}', portfolio='{}', id='{}')>".format(
            self.name, self.description, self.portfolio.name, self.id
        )

    @property
    def history(self):
        return self.get_changes()
