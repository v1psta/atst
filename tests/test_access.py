from unittest.mock import Mock

import pytest

from flask import url_for, Response

import atst
from atst.app import make_app, make_config
from atst.domain.auth import UNPROTECTED_ROUTES as _NO_LOGIN_REQUIRED
from atst.domain.permission_sets import PermissionSets
from atst.models import CSPRole, PortfolioRoleStatus, ApplicationRoleStatus

from tests.factories import *

_NO_ACCESS_CHECK_REQUIRED = _NO_LOGIN_REQUIRED + [
    "applications.accept_invitation",  # available to all users; access control is built into invitation logic
    "atst.catch_all",  # available to all users
    "atst.csp_environment_access",  # internal redirect
    "atst.home",  # available to all users
    "atst.jedi_csp_calculator",  # internal redirect
    "atst.styleguide",  # dev reference
    "dev.messages",  # dev tool
    "dev.test_email",  # dev tool
    "portfolios.accept_invitation",  # available to all users; access control is built into invitation logic
    "portfolios.create_portfolio",  # create a portfolio
    "portfolios.new_portfolio",  # all users can create a portfolio
    "portfolios.portfolios",  # the portfolios list is scoped to the user separately
    "task_orders.get_started",  # all users can start a new TO
    "users.update_user",  # available to all users
    "users.user",  # available to all users
]


def protected_routes(app):
    _protected_routes = []

    for rule in app.url_map.iter_rules():
        args = [1] * len(rule.arguments)
        mock_args = dict(zip(rule.arguments, args))
        _n, route = rule.build(mock_args)
        if rule.endpoint in _NO_ACCESS_CHECK_REQUIRED or "/static" in route:
            continue

        _protected_routes.append((rule, route))

    return _protected_routes


sample_config = make_config({"CRL_STORAGE_PROVIDER": "LOCAL"})
sample_app = make_app(sample_config)
_PROTECTED_ROUTES = protected_routes(sample_app)


@pytest.mark.access_check
@pytest.mark.parametrize("rule,route", _PROTECTED_ROUTES)
def test_all_protected_routes_have_access_control(
    rule, route, mocker, client, user_session, monkeypatch
):
    """
    This tests that all routes, except the ones in
    _NO_ACCESS_CHECK_REQUIRED, are protected by the access
    decorator.
    """
    # monkeypatch any object lookups that might happen in the access decorator
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.for_user", lambda *a: [])
    monkeypatch.setattr("atst.domain.portfolios.Portfolios.get", lambda *a: None)
    monkeypatch.setattr("atst.domain.task_orders.TaskOrders.get", lambda *a: Mock())
    monkeypatch.setattr("atst.domain.applications.Applications.get", lambda *a: Mock())
    monkeypatch.setattr(
        "atst.domain.invitations.PortfolioInvitations._get", lambda *a: Mock()
    )
    monkeypatch.setattr("atst.app.assign_resources", lambda *a: None)

    # patch the internal function the access decorator uses so that
    # we can check that it was called
    mocker.patch("atst.domain.authz.decorator.check_access")

    user = UserFactory.create()
    user_session(user)

    method = "get" if "GET" in rule.methods else "post"
    getattr(client, method)(route)

    assert (
        atst.domain.authz.decorator.check_access.call_count == 1
    ), "no access control for {}".format(rule.endpoint)


def user_with(*perm_sets_names):
    return UserFactory.create(permission_sets=PermissionSets.get_many(perm_sets_names))


@pytest.fixture
def get_url_assert_status(client, user_session):
    def _get_url_assert_status(user, url, status):
        user_session(user)
        resp = client.get(url)
        assert resp.status_code == status

    return _get_url_assert_status


@pytest.fixture
def post_url_assert_status(client, user_session):
    def _get_url_assert_status(user, url, status, data=None):
        user_session(user)
        resp = client.post(url, data=data)
        assert resp.status_code == status

    return _get_url_assert_status


# atst.activity_history
def test_atst_activity_history_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_AUDIT_LOG)
    rando = user_with()

    url = url_for("atst.activity_history")
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.access_environment
def test_applications_access_environment_access(get_url_assert_status):
    dev = UserFactory.create()
    rando = UserFactory.create()
    ccpo = UserFactory.create_ccpo()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[
            {
                "name": "Mos Eisley",
                "description": "Where Han shot first",
                "environments": [
                    {
                        "name": "thebar",
                        "members": [{"user": dev, "role_name": "devops"}],
                    }
                ],
            }
        ],
    )
    env = portfolio.applications[0].environments[0]

    url = url_for("applications.access_environment", environment_id=env.id)
    get_url_assert_status(dev, url, 302)
    get_url_assert_status(rando, url, 404)
    get_url_assert_status(ccpo, url, 404)


# applications.create
def test_applications_create_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("applications.create", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# applications.update_env_roles
def test_applications_update_team_env_roles(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    app_admin = user_with()
    rando = user_with()
    app_member = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=owner, applications=[{"name": "mos eisley"}]
    )
    application = portfolio.applications[0]
    environment = EnvironmentFactory.create(application=application)

    ApplicationRoleFactory.create(
        user=app_admin,
        application=application,
        permission_sets=PermissionSets.get_many(
            [
                PermissionSets.VIEW_APPLICATION,
                PermissionSets.EDIT_APPLICATION_ENVIRONMENTS,
                PermissionSets.EDIT_APPLICATION_TEAM,
                PermissionSets.DELETE_APPLICATION_ENVIRONMENTS,
            ]
        ),
    )
    ApplicationRoleFactory.create(user=app_member, application=application)
    ApplicationRoleFactory.create(user=ccpo, application=application)
    ApplicationRoleFactory.create(user=owner, application=application)

    url = url_for("applications.update_env_roles", environment_id=environment.id)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(app_admin, url, 302)
    post_url_assert_status(rando, url, 404)


# portfolios.invite_member
def test_portfolios_invite_member_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.invite_member", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(rando, url, 404)


# applications.delete
def test_applications_delete_access(post_url_assert_status, monkeypatch):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    app_admin = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(
        owner=owner, applications=[{"name": "mos eisley"}]
    )
    application = portfolio.applications[0]

    ApplicationRoleFactory.create(
        user=app_admin,
        application=application,
        permission_sets=PermissionSets.get_many(
            [
                PermissionSets.VIEW_APPLICATION,
                PermissionSets.EDIT_APPLICATION_ENVIRONMENTS,
                PermissionSets.EDIT_APPLICATION_TEAM,
                PermissionSets.DELETE_APPLICATION_ENVIRONMENTS,
            ]
        ),
    )

    monkeypatch.setattr("atst.domain.applications.Applications.delete", lambda *a: True)

    url = url_for("applications.delete", application_id=application.id)
    post_url_assert_status(app_admin, url, 404)
    post_url_assert_status(rando, url, 404)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(ccpo, url, 302)


# applications.settings
def test_application_settings_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for("applications.settings", application_id=app.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.edit
def test_portfolios_edit_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.edit", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# applications.new
def test_applications_new_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("applications.new", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.admin
def test_portfolios_admin_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.admin", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# applications.portfolio_applications
def test_applications_portfolio_applications_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    app_user = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    application = ApplicationFactory.create(portfolio=portfolio)
    ApplicationRoleFactory.create(
        application=application, user=app_user, status=ApplicationRoleStatus.ACTIVE
    )

    url = url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(app_user, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.portfolio_funding
def test_task_orders_portfolio_funding_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("task_orders.portfolio_funding", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.reports
def test_portfolios_portfolio_reports_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.reports", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.resend_invitation
def test_portfolios_resend_invitation_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    invitee = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    prr = PortfolioRoleFactory.create(user=invitee, portfolio=portfolio)
    invite = PortfolioInvitationFactory.create(user=UserFactory.create(), role=prr)

    url = url_for(
        "portfolios.resend_invitation",
        portfolio_id=portfolio.id,
        portfolio_token=invite.token,
    )
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(invitee, url, 404)
    post_url_assert_status(rando, url, 404)


# portfolios.revoke_invitation
def test_portfolios_revoke_invitation_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)

    for user, status in [(ccpo, 302), (owner, 302), (rando, 404)]:
        prt_member = user_with()
        prr = PortfolioRoleFactory.create(
            user=prt_member, portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
        )
        invite = PortfolioInvitationFactory.create(user=prt_member, role=prr)
        url = url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            portfolio_token=invite.token,
        )
        post_url_assert_status(user, url, status)


# applications.update
def test_applications_update_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    dev = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for("applications.update", application_id=app.id)
    post_url_assert_status(dev, url, 200)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(rando, url, 404)


# applications.update_environments
def test_applications_update_environments(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    dev = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]
    environment = EnvironmentFactory.create(application=app)

    url = url_for("applications.update_environment", environment_id=environment.id)
    post_url_assert_status(dev, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)


# task_orders.download_task_order_pdf
def test_task_orders_download_task_order_pdf_access(get_url_assert_status, monkeypatch):
    monkeypatch.setattr(
        "atst.routes.task_orders.downloads.send_file", lambda a: Response("")
    )
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, pdf=AttachmentFactory.create()
    )

    url = url_for("task_orders.download_task_order_pdf", task_order_id=task_order.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.update
def test_task_orders_update_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    data = {"number": 1234567890}

    url = url_for("task_orders.update", portfolio_id=portfolio.id)
    post_url_assert_status(owner, url, 302, data=data)
    post_url_assert_status(ccpo, url, 302, data=data)
    post_url_assert_status(rando, url, 404, data=data)

    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.update", task_order_id=task_order.id)
    post_url_assert_status(owner, url, 302, data=data)
    post_url_assert_status(ccpo, url, 302, data=data)
    post_url_assert_status(rando, url, 404, data=data)

    url = url_for("task_orders.update", portfolio_id=portfolio.id)
    post_url_assert_status(owner, url, 302, data=data)
    post_url_assert_status(ccpo, url, 302, data=data)
    post_url_assert_status(rando, url, 404, data=data)


def test_applications_application_team_access(get_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)

    url = url_for("applications.team", application_id=application.id)

    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(portfolio.owner, url, 200)
    get_url_assert_status(rando, url, 404)


def test_portfolio_delete_access(post_url_assert_status):
    rando = UserFactory.create()
    owner = UserFactory.create()
    ccpo = UserFactory.create_ccpo()

    post_url_assert_status(
        ccpo,
        url_for(
            "portfolios.delete_portfolio", portfolio_id=PortfolioFactory.create().id
        ),
        302,
    )

    post_url_assert_status(
        owner,
        url_for(
            "portfolios.delete_portfolio",
            portfolio_id=PortfolioFactory.create(owner=owner).id,
        ),
        302,
    )

    post_url_assert_status(
        rando,
        url_for(
            "portfolios.delete_portfolio", portfolio_id=PortfolioFactory.create().id
        ),
        404,
    )
