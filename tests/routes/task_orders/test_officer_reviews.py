import pytest
from flask import url_for

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models.portfolio_role import Status as PortfolioStatus

from tests.factories import (
    PortfolioFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
    DD254Factory,
)
from tests.utils import captured_templates


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


def test_ko_can_view_ko_review_page(client, user_session):
    portfolio = PortfolioFactory.create()
    ko = UserFactory.create()
    cor = UserFactory.create()

    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=cor,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(
        portfolio=portfolio,
        contracting_officer=ko,
        contracting_officer_representative=cor,
    )
    request_url = url_for("task_orders.ko_review", task_order_id=task_order.id)

    #
    # KO returns 200
    #
    user_session(ko)
    response = client.get(request_url)
    assert response.status_code == 200

    #
    # COR returns 200
    #
    user_session(cor)
    response = client.get(request_url)
    assert response.status_code == 200

    #
    # Random user raises UnauthorizedError
    #
    user_session(UserFactory.create())
    response = client.get(request_url)
    assert response.status_code == 404


def test_cor_cant_view_review_until_to_completed(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, clin_01=None, cor_dod_id=portfolio.owner.dod_id
    )
    response = client.get(url_for("task_orders.ko_review", task_order_id=task_order.id))
    assert response.status_code == 404


def test_submit_completed_ko_review_page_as_cor(
    client, user_session, pdf_upload, portfolio, user
):
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=user,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer_representative=user
    )

    form_data = {
        "start_date": "02/10/2019",
        "end_date": "03/10/2019",
        "number": "1938745981",
        "loas-0": "0813458013405",
        "custom_clauses": "hi im a custom clause",
        "pdf": pdf_upload,
    }

    user_session(user)

    response = client.post(
        url_for("task_orders.ko_review", task_order_id=task_order.id), data=form_data
    )

    assert task_order.pdf
    assert response.headers["Location"] == url_for(
        "task_orders.view_task_order", task_order_id=task_order.id, _external=True
    )


def test_submit_completed_ko_review_page_as_ko(
    client, user_session, pdf_upload, portfolio
):
    ko = UserFactory.create()

    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )

    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    dd_254 = DD254Factory.create()
    TaskOrders.add_dd_254(task_order, dd_254.to_dictionary())
    user_session(ko)
    loa_list = ["123123123", "456456456", "789789789"]

    form_data = {
        "start_date": "02/10/2019",
        "end_date": "03/10/2019",
        "number": "1938745981",
        "loas-0": loa_list[0],
        "loas-1": loa_list[1],
        "loas-2": loa_list[2],
        "custom_clauses": "hi im a custom clause",
        "pdf": pdf_upload,
    }

    response = client.post(
        url_for("task_orders.ko_review", task_order_id=task_order.id), data=form_data
    )
    assert task_order.pdf
    assert response.headers["Location"] == url_for(
        "task_orders.signature_requested", task_order_id=task_order.id, _external=True
    )
    assert task_order.loas == loa_list


def test_ko_can_only_access_their_to(app, user_session, client, portfolio, pdf_upload):
    ko = UserFactory.create()

    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=ko,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )

    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=ko)
    dd_254 = DD254Factory.create()
    TaskOrders.add_dd_254(task_order, dd_254.to_dictionary())
    other_task_order = TaskOrderFactory.create()
    user_session(ko)

    # KO can't see TO
    response = client.get(
        url_for("task_orders.ko_review", task_order_id=other_task_order.id)
    )
    assert response.status_code == 404

    # KO can't submit review for TO
    form_data = {
        "start_date": "02/10/2019",
        "end_date": "03/10/2019",
        "number": "1938745981",
        "loas-0": "1231231231",
        "custom_clauses": "hi im a custom clause",
        "pdf": pdf_upload,
    }

    response = client.post(
        url_for("task_orders.submit_ko_review", task_order_id=other_task_order.id),
        data=form_data,
    )
    assert response.status_code == 404
    assert not TaskOrders.is_signed_by_ko(other_task_order)


def test_so_review_page(app, client, user_session, portfolio):
    so = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=so,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)

    user_session(portfolio.owner)
    owner_response = client.get(
        url_for("task_orders.so_review", task_order_id=task_order.id)
    )
    assert owner_response.status_code == 404

    with captured_templates(app) as templates:
        user_session(so)
        so_response = app.test_client().get(
            url_for("task_orders.so_review", task_order_id=task_order.id)
        )
        _, context = templates[0]
        form = context["form"]
        co_name = form.certifying_official.data
        assert so_response.status_code == 200
        assert (
            task_order.so_first_name in co_name and task_order.so_last_name in co_name
        )


def test_submit_so_review(app, client, user_session, portfolio):
    so = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=so,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)
    dd_254_data = DD254Factory.dictionary()

    user_session(so)
    response = client.post(
        url_for("task_orders.submit_so_review", task_order_id=task_order.id),
        data=dd_254_data,
    )
    expected_redirect = url_for(
        "task_orders.view_task_order", task_order_id=task_order.id, _external=True
    )
    assert response.status_code == 302
    assert response.headers["Location"] == expected_redirect

    assert task_order.dd_254
    assert task_order.dd_254.certifying_official == dd_254_data["certifying_official"]


def test_so_can_only_access_their_to(app, client, user_session, portfolio):
    so = UserFactory.create()
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=so,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, security_officer=so)
    dd_254_data = DD254Factory.dictionary()
    other_task_order = TaskOrderFactory.create()
    user_session(so)

    # SO can't view dd254
    response = client.get(
        url_for("task_orders.so_review", task_order_id=other_task_order.id)
    )
    assert response.status_code == 404

    # SO can't submit dd254
    response = client.post(
        url_for("task_orders.submit_so_review", task_order_id=other_task_order.id),
        data=dd_254_data,
    )
    assert response.status_code == 404
    assert not other_task_order.dd_254
