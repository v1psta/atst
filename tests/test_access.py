from unittest.mock import Mock

import pytest

from flask import url_for, Response

import atst
from atst.app import make_app, make_config
from atst.domain.auth import UNPROTECTED_ROUTES as _NO_LOGIN_REQUIRED
from atst.domain.permission_sets import PermissionSets
from atst.models.portfolio_role import Status as PortfolioRoleStatus

from tests.factories import (
    AttachmentFactory,
    InvitationFactory,
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
)

_NO_ACCESS_CHECK_REQUIRED = _NO_LOGIN_REQUIRED + [
    "task_orders.get_started",  # all users can start a new TO
    "atst.csp_environment_access",  # internal redirect
    "atst.jedi_csp_calculator",  # internal redirect
    "atst.styleguide",  # dev reference
    "dev.test_email",  # dev tool
    "dev.messages",  # dev tool
    "atst.home",  # available to all users
    "users.user",  # available to all users
    "users.update_user",  # available to all users
    "portfolios.accept_invitation",  # available to all users; access control is built into invitation logic
    "atst.catch_all",  # available to all users
    "portfolios.portfolios",  # the portfolios list is scoped to the user separately
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
    def _get_url_assert_status(user, url, status):
        user_session(user)
        resp = client.post(url)
        assert resp.status_code == status

    return _get_url_assert_status


# atst.activity_history
def test_atst_activity_history_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_AUDIT_LOG)
    rando = user_with()

    url = url_for("atst.activity_history")
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.access_environment
def test_portfolios_access_environment_access(get_url_assert_status):
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

    url = url_for(
        "portfolios.access_environment",
        portfolio_id=portfolio.id,
        environment_id=env.id,
    )
    get_url_assert_status(dev, url, 302)
    get_url_assert_status(rando, url, 404)
    get_url_assert_status(ccpo, url, 404)


# portfolios.application_members
def test_portfolios_application_members_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for(
        "portfolios.application_members",
        portfolio_id=portfolio.id,
        application_id=app.id,
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.create_application
def test_portfolios_create_application_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.create_application", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# portfolios.create_member
def test_portfolios_create_member_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.create_member", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# portfolios.edit_application
def test_portfolios_edit_application_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for(
        "portfolios.edit_application", portfolio_id=portfolio.id, application_id=app.id
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.edit_portfolio
def test_portfolios_edit_portfolio_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.edit_portfolio", portfolio_id=portfolio.id)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(rando, url, 404)


# portfolios.edit_task_order_invitations
def test_portfolios_edit_task_order_invitations_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for(
        "portfolios.edit_task_order_invitations",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
    )
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(rando, url, 404)


# portfolios.ko_review
def test_portfolios_ko_review_access(get_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    cor = user_with()
    ko = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        contracting_officer=ko,
        contracting_officer_representative=cor,
    )

    url = url_for(
        "portfolios.ko_review", portfolio_id=portfolio.id, task_order_id=task_order.id
    )
    get_url_assert_status(ccpo, url, 404)
    get_url_assert_status(owner, url, 404)
    get_url_assert_status(ko, url, 200)
    get_url_assert_status(cor, url, 200)


# portfolios.new_application
def test_portfolios_new_application_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.new_application", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.new_member
def test_portfolios_new_member_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.new_member", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.portfolio_admin
def test_portfolios_portfolio_admin_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.portfolio_admin", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.portfolio_applications
def test_portfolios_portfolio_applications_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_APPLICATION_MANAGEMENT)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.portfolio_applications", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.portfolio_funding
def test_portfolios_portfolio_funding_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.portfolio_members
def test_portfolios_portfolio_members_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.portfolio_members", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.portfolio_reports
def test_portfolios_portfolio_reports_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_REPORTS)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.portfolio_reports", portfolio_id=portfolio.id)
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
    invite = InvitationFactory.create(user=UserFactory.create(), portfolio_role=prr)

    url = url_for(
        "portfolios.resend_invitation", portfolio_id=portfolio.id, token=invite.token
    )
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(invitee, url, 404)
    post_url_assert_status(rando, url, 404)


# portfolios.resend_invite
def test_portfolios_resend_invite_access(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    rando = user_with()
    ko = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    prr = PortfolioRoleFactory.create(user=ko, portfolio=portfolio)
    invite = InvitationFactory.create(user=UserFactory.create(), portfolio_role=prr)

    url = url_for(
        "portfolios.resend_invite",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
        invite_type="ko_invite",
    )
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(ko, url, 404)
    post_url_assert_status(rando, url, 404)


# portfolios.revoke_access
def test_portfolios_revoke_access_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)

    for user, status in [(ccpo, 302), (owner, 302), (rando, 404)]:
        prt_member = user_with()
        prr = PortfolioRoleFactory.create(
            user=prt_member, portfolio=portfolio, status=PortfolioRoleStatus.ACTIVE
        )
        url = url_for(
            "portfolios.revoke_access", portfolio_id=portfolio.id, member_id=prr.id
        )
        post_url_assert_status(user, url, status)


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
        invite = InvitationFactory.create(user=prt_member, portfolio_role=prr)
        url = url_for(
            "portfolios.revoke_invitation",
            portfolio_id=portfolio.id,
            token=invite.token,
        )
        post_url_assert_status(user, url, status)


# portfolios.show_portfolio
def test_portfolios_show_portfolio_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)

    url = url_for("portfolios.show_portfolio", portfolio_id=portfolio.id)
    get_url_assert_status(ccpo, url, 302)
    get_url_assert_status(owner, url, 302)
    get_url_assert_status(rando, url, 404)


# portfolios.so_review
def test_portfolios_so_review_access(get_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    rando = user_with()
    so = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)

    url = url_for(
        "portfolios.so_review", portfolio_id=portfolio.id, task_order_id=task_order.id
    )
    get_url_assert_status(so, url, 200)
    get_url_assert_status(ccpo, url, 404)
    get_url_assert_status(owner, url, 404)
    get_url_assert_status(rando, url, 404)


# portfolios.submit_ko_review
def test_portfolios_submit_ko_review_access(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    cor = user_with()
    ko = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        contracting_officer=ko,
        contracting_officer_representative=cor,
    )

    url = url_for(
        "portfolios.submit_ko_review",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
    )
    post_url_assert_status(ccpo, url, 404)
    post_url_assert_status(owner, url, 404)
    post_url_assert_status(ko, url, 200)
    post_url_assert_status(cor, url, 200)


# portfolios.submit_so_review
def test_portfolios_submit_so_review_access(post_url_assert_status):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    rando = user_with()
    so = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)

    url = url_for(
        "portfolios.submit_so_review",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
    )
    post_url_assert_status(so, url, 200)
    post_url_assert_status(ccpo, url, 404)
    post_url_assert_status(owner, url, 404)
    post_url_assert_status(rando, url, 404)


# portfolios.task_order_invitations
def test_portfolios_task_order_invitations_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()
    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for(
        "portfolios.task_order_invitations",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
    )
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.update_application
def test_portfolios_update_application_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT)
    dev = UserFactory.create()
    rando = UserFactory.create()

    portfolio = PortfolioFactory.create(
        owner=dev,
        applications=[{"name": "Mos Eisley", "description": "Where Han shot first"}],
    )
    app = portfolio.applications[0]

    url = url_for(
        "portfolios.update_application",
        portfolio_id=portfolio.id,
        application_id=app.id,
    )
    post_url_assert_status(dev, url, 200)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(rando, url, 404)


# portfolios.update_member
def test_portfolios_update_member_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    prt_member = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    prr = PortfolioRoleFactory.create(user=prt_member, portfolio=portfolio)

    url = url_for(
        "portfolios.update_member", portfolio_id=portfolio.id, member_id=prt_member.id
    )
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(rando, url, 404)


# portfolios.view_member
def test_portfolios_view_member_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_ADMIN)
    owner = user_with()
    rando = user_with()
    prt_member = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    prr = PortfolioRoleFactory.create(user=prt_member, portfolio=portfolio)

    url = url_for(
        "portfolios.view_member", portfolio_id=portfolio.id, member_id=prt_member.id
    )
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# portfolios.view_task_order
def test_portfolios_view_task_order_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for(
        "portfolios.view_task_order",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
    )
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.download_csp_estimate
def test_task_orders_download_csp_estimate_access(get_url_assert_status, monkeypatch):
    monkeypatch.setattr(
        "atst.routes.task_orders.index.send_file", lambda a: Response("")
    )
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.download_csp_estimate", task_order_id=task_order.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.download_summary
def test_task_orders_download_summary_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.VIEW_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.download_summary", task_order_id=task_order.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.download_task_order_pdf
def test_task_orders_download_task_order_pdf_access(get_url_assert_status, monkeypatch):
    monkeypatch.setattr(
        "atst.routes.task_orders.index.send_file", lambda a: Response("")
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


# task_orders.invite
def test_task_orders_invite_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.invite", task_order_id=task_order.id)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)


# task_orders.new
def test_task_orders_new_access(get_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    url = url_for("task_orders.new", screen=1)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 200)

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.new", screen=2, task_order_id=task_order.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)

    url = url_for("task_orders.new", screen=1, portfolio_id=portfolio.id)
    get_url_assert_status(owner, url, 200)
    get_url_assert_status(ccpo, url, 200)
    get_url_assert_status(rando, url, 404)


# task_orders.record_signature
def test_task_orders_record_signature_access(post_url_assert_status, monkeypatch):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    rando = user_with()
    ko = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    monkeypatch.setattr(
        "atst.routes.task_orders.signing.find_unsigned_ko_to", lambda *a: task_order
    )

    url = url_for("task_orders.record_signature", task_order_id=task_order.id)
    post_url_assert_status(ko, url, 400)
    post_url_assert_status(owner, url, 404)
    post_url_assert_status(ccpo, url, 404)
    post_url_assert_status(rando, url, 404)


# task_orders.signature_requested
def test_task_orders_signature_requested_access(get_url_assert_status, monkeypatch):
    ccpo = UserFactory.create_ccpo()
    owner = user_with()
    rando = user_with()
    ko = user_with()

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    monkeypatch.setattr(
        "atst.routes.task_orders.signing.find_unsigned_ko_to", lambda *a: task_order
    )

    url = url_for("task_orders.record_signature", task_order_id=task_order.id)
    get_url_assert_status(ko, url, 200)
    get_url_assert_status(owner, url, 404)
    get_url_assert_status(ccpo, url, 404)
    get_url_assert_status(rando, url, 404)


# task_orders.update
def test_task_orders_update_access(post_url_assert_status):
    ccpo = user_with(PermissionSets.EDIT_PORTFOLIO_FUNDING)
    owner = user_with()
    rando = user_with()

    url = url_for("task_orders.update", screen=1)
    post_url_assert_status(owner, url, 200)
    post_url_assert_status(ccpo, url, 200)
    post_url_assert_status(rando, url, 200)

    portfolio = PortfolioFactory.create(owner=owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    url = url_for("task_orders.update", screen=2, task_order_id=task_order.id)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)

    url = url_for("task_orders.update", screen=1, portfolio_id=portfolio.id)
    post_url_assert_status(owner, url, 302)
    post_url_assert_status(ccpo, url, 302)
    post_url_assert_status(rando, url, 404)
