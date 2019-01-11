from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.common import Query
from atst.domain.exceptions import NotFoundError
from atst.models.portfolio import Portfolio
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus


class PortfoliosQuery(Query):
    model = Portfolio

    @classmethod
    def get_by_request(cls, request):
        try:
            portfolio = db.session.query(Portfolio).filter_by(request=request).one()
        except NoResultFound:
            raise NotFoundError("portfolio")

        return portfolio

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
