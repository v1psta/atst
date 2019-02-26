from atst.database import db
from atst.domain.common import Query
from atst.models.portfolio import Portfolio
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus


class PortfoliosQuery(Query):
    model = Portfolio

    @classmethod
    def get_for_user(cls, user):
        return (
            db.session.query(Portfolio)
            .join(PortfolioRole)
            .filter(PortfolioRole.user == user)
            .filter(PortfolioRole.status == PortfolioRoleStatus.ACTIVE)
            .all()
        )

    @classmethod
    def create_portfolio_role(cls, user, role, portfolio, **kwargs):
        return PortfolioRole(user=user, role=role, portfolio=portfolio, **kwargs)
