from atst.database import db
from atst.domain.common import Query
from atst.models.portfolio import Portfolio
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atst.models.application_role import (
    ApplicationRole,
    Status as ApplicationRoleStatus,
)
from atst.models.application import Application


class PortfoliosQuery(Query):
    model = Portfolio

    @classmethod
    def get_for_user(cls, user):
        granted_applications = (
            db.session.query(Application)
            .join(ApplicationRole)
            .filter(ApplicationRole.application_id == Application.id)
            .filter(ApplicationRole.user_id == user.id)
            .filter(ApplicationRole.status == ApplicationRoleStatus.ACTIVE)
            .subquery()
        )

        application_portfolios = (
            db.session.query(Portfolio)
            .join(Application)
            .filter(Portfolio.id == Application.portfolio_id)
            .filter(Application.id == granted_applications.c.id)
            .all()
        )

        portfolios = (
            db.session.query(Portfolio)
            .join(PortfolioRole)
            .filter(PortfolioRole.user == user)
            .filter(PortfolioRole.status == PortfolioRoleStatus.ACTIVE)
            .all()
        )

        portfolio_ids = []

        [portfolio_ids.append(p.id) for p in portfolios]
        [portfolio_ids.append(p.id) for p in application_portfolios]

        return (
            db.session.query(Portfolio)
            .filter(Portfolio.id.in_(portfolio_ids))
            .order_by(Portfolio.name.desc())
            .all()
        )

    @classmethod
    def create_portfolio_role(cls, user, portfolio, **kwargs):
        return PortfolioRole(user=user, portfolio=portfolio, **kwargs)
