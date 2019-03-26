from flask import url_for

from atst.domain.permission_sets import PermissionSets

from tests.factories import PortfolioFactory, PortfolioRoleFactory, UserFactory


def test_member_table_access(client, user_session):
    admin = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=admin)
    rando = UserFactory.create()
    PortfolioRoleFactory.create(
        user=rando,
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_ADMIN)],
    )

    url = url_for("portfolios.portfolio_admin", portfolio_id=portfolio.id)

    # editable
    user_session(admin)
    edit_resp = client.get(url)
    assert "<select" in edit_resp.data.decode()

    # not editable
    user_session(rando)
    view_resp = client.get(url)
    assert "<select" not in view_resp.data.decode()
