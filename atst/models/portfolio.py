from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from itertools import chain

from atst.models import Base, mixins, types
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atst.utils import first_or_none
from atst.database import db


class Portfolio(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "workspaces"

    id = types.Id()
    name = Column(String)
    request_id = Column(ForeignKey("requests.id"), nullable=True)
    applications = relationship("Application", back_populates="portfolio")
    roles = relationship("PortfolioRole")

    task_orders = relationship("TaskOrder")

    @property
    def owner(self):
        def _is_portfolio_owner(portfolio_role):
            return portfolio_role.role.name == "owner"

        owner = first_or_none(_is_portfolio_owner, self.roles)
        return owner.user if owner else None

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.members)

    @property
    def legacy_task_order(self):
        return self.request.legacy_task_order if self.request else None

    @property
    def members(self):
        return (
            db.session.query(PortfolioRole)
            .filter(PortfolioRole.portfolio_id == self.id)
            .filter(PortfolioRole.status != PortfolioRoleStatus.DISABLED)
            .all()
        )

    @property
    def displayname(self):
        return self.name

    @property
    def all_environments(self):
        return list(chain.from_iterable(p.environments for p in self.applications))

    def auditable_portfolio_id(self):
        return self.id

    def __repr__(self):
        return "<Portfolio(name='{}', request='{}', user_count='{}', id='{}')>".format(
            self.name, self.request_id, self.user_count, self.id
        )
