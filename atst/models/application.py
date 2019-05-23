from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, synonym

from atst.models import Base
from atst.models.types import Id
from atst.models import mixins


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
    roles = relationship(
        "ApplicationRole",
        primaryjoin="and_(ApplicationRole.application_id==Application.id, ApplicationRole.deleted==False)",
    )
    members = synonym("roles")

    @property
    def users(self):
        return set(role.user for role in self.members)

    @property
    def displayname(self):
        return self.name

    @property
    def application_id(self):
        return self.id

    def __repr__(self):  # pragma: no cover
        return "<Application(name='{}', description='{}', portfolio='{}', id='{}')>".format(
            self.name, self.description, self.portfolio.name, self.id
        )

    @property
    def history(self):
        return self.get_changes()
