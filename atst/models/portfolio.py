from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from itertools import chain

from atst.models import Base, mixins, types
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atst.domain.permission_sets import PermissionSets
from atst.utils import first_or_none
from atst.database import db


class Portfolio(Base, mixins.TimestampsMixin, mixins.AuditableMixin):
    __tablename__ = "portfolios"

    id = types.Id()
    name = Column(String)
    defense_component = Column(String)  # Department of Defense Component

    applications = relationship("Application", back_populates="portfolio")
    roles = relationship("PortfolioRole")

    task_orders = relationship("TaskOrder")

    @property
    def owner(self):
        def _is_portfolio_owner(portfolio_role):
            return PermissionSets.PORTFOLIO_POC in [
                perms_set.name for perms_set in portfolio_role.permission_sets
            ]

        owner = first_or_none(_is_portfolio_owner, self.roles)
        return owner.user if owner else None

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.members)

    @property
    def num_task_orders(self):
        return len(self.task_orders)

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
        return "<Portfolio(name='{}', user_count='{}', id='{}')>".format(
            self.name, self.user_count, self.id
        )
