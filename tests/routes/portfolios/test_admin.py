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


def test_update_member_permissions(client, user_session):
    portfolio = PortfolioFactory.create()
    rando = UserFactory.create()
    rando_pf_role = PortfolioRoleFactory.create(
        user=rando,
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_ADMIN)],
    )

    user = UserFactory.create()
    PortfolioRoleFactory.create(
        user=user,
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.EDIT_PORTFOLIO_ADMIN)],
    )
    user_session(user)

    form_data = {
        "members_permissions-0-user_id": rando.id,
        "members_permissions-0-perms_app_mgmt": "edit_portfolio_application_management",
        "members_permissions-0-perms_funding": "view_portfolio_funding",
        "members_permissions-0-perms_reporting": "view_portfolio_reports",
        "members_permissions-0-perms_portfolio_mgmt": "view_portfolio_admin",
    }

    response = client.post(
        url_for("portfolios.edit_portfolio_members", portfolio_id=portfolio.id),
        data=form_data,
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert rando_pf_role.has_permission_set(
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT
    )


def test_no_update_member_permissions_without_edit_access(client, user_session):
    portfolio = PortfolioFactory.create()
    rando = UserFactory.create()
    rando_pf_role = PortfolioRoleFactory.create(
        user=rando,
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_ADMIN)],
    )

    user = UserFactory.create()
    PortfolioRoleFactory.create(
        user=user,
        portfolio=portfolio,
        permission_sets=[PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_ADMIN)],
    )
    user_session(user)

    form_data = {
        "members_permissions-0-user_id": rando.id,
        "members_permissions-0-perms_app_mgmt": "edit_portfolio_application_management",
        "members_permissions-0-perms_funding": "view_portfolio_funding",
        "members_permissions-0-perms_reporting": "view_portfolio_reports",
        "members_permissions-0-perms_portfolio_mgmt": "view_portfolio_admin",
    }

    response = client.post(
        url_for("portfolios.edit_portfolio_members", portfolio_id=portfolio.id),
        data=form_data,
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert not rando_pf_role.has_permission_set(
        PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT
    )
