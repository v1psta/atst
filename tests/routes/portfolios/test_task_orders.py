from flask import url_for
import pytest
from datetime import timedelta, date, datetime

from atst.domain.permission_sets import PermissionSets
from atst.domain.task_orders import TaskOrders
from atst.models.portfolio_role import Status as PortfolioStatus
from atst.models.invitation import Status as InvitationStatus
from atst.utils.localization import translate
from atst.queue import queue
from atst.domain.invitations import Invitations

from tests.factories import (
    PortfolioFactory,
    InvitationFactory,
    PortfolioRoleFactory,
    TaskOrderFactory,
    UserFactory,
    DD254Factory,
    random_future_date,
    random_past_date,
)
from tests.utils import captured_templates


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


class TestPortfolioFunding:
    def test_portfolio_with_no_task_orders(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is None
            assert context["total_balance"] == 0
            assert context["pending_task_orders"] == []
            assert context["active_task_orders"] == []
            assert context["expired_task_orders"] == []

    def test_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        pending_to = TaskOrderFactory.create(portfolio=portfolio)
        active_to1 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="42",
        )
        active_to2 = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(),
            number="43",
        )
        end_date = (
            active_to1.end_date
            if active_to1.end_date > active_to2.end_date
            else active_to2.end_date
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is end_date
            assert context["total_balance"] == active_to1.budget + active_to2.budget

    def test_expiring_and_funded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )
        active_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=random_future_date(year_min=1, year_max=2),
            number="43",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is active_to.end_date
            assert context["funded"] == True

    def test_expiring_and_unfunded_portfolio(self, app, user_session, portfolio):
        user_session(portfolio.owner)

        expiring_to = TaskOrderFactory.create(
            portfolio=portfolio,
            start_date=random_past_date(),
            end_date=(date.today() + timedelta(days=10)),
            number="42",
        )

        with captured_templates(app) as templates:
            response = app.test_client().get(
                url_for("portfolios.portfolio_funding", portfolio_id=portfolio.id)
            )

            assert response.status_code == 200
            _, context = templates[0]
            assert context["funding_end_date"] is expiring_to.end_date
            assert context["funded"] == False

    def test_user_can_only_access_to_in_their_portfolio(
        self, app, user_session, portfolio
    ):
        other_task_order = TaskOrderFactory.create()
        user_session(portfolio.owner)
        response = app.test_client().get(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=portfolio.id,
                task_order_id=other_task_order.id,
            )
        )
        assert response.status_code == 404


class TestTaskOrderInvitations:
    def setup(self):
        self.portfolio = PortfolioFactory.create()
        self.task_order = TaskOrderFactory.create(portfolio=self.portfolio)

    def _post(self, client, updates):
        return client.post(
            url_for(
                "portfolios.edit_task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=self.task_order.id,
            ),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=updates,
        )

    def test_editing_with_partial_data(self, user_session, client):
        queue_length = len(queue.get_queue())
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-first_name": "Luke",
                "contracting_officer-last_name": "Skywalker",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )
        updated_task_order = TaskOrders.get(self.task_order.id)
        assert updated_task_order.ko_first_name == "Luke"
        assert updated_task_order.ko_last_name == "Skywalker"
        assert updated_task_order.so_first_name == "Boba"
        assert updated_task_order.so_last_name == "Fett"
        assert len(queue.get_queue()) == queue_length
        assert response.status_code == 302
        assert (
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=self.task_order.id,
                _external=True,
            )
            == response.headers["Location"]
        )

    def test_editing_with_complete_data(self, user_session, client):
        queue_length = len(queue.get_queue())

        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-first_name": "Luke",
                "contracting_officer-last_name": "Skywalker",
                "contracting_officer-dod_id": "0123456789",
                "contracting_officer-email": "luke@skywalker.mil",
                "contracting_officer-phone_number": "0123456789",
                "contracting_officer-invite": "y",
            },
        )
        updated_task_order = TaskOrders.get(self.task_order.id)

        assert updated_task_order.ko_invite == True
        assert updated_task_order.ko_first_name == "Luke"
        assert updated_task_order.ko_last_name == "Skywalker"
        assert updated_task_order.ko_email == "luke@skywalker.mil"
        assert updated_task_order.ko_phone_number == "0123456789"
        assert len(queue.get_queue()) == queue_length + 1
        assert response.status_code == 302
        assert (
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=self.task_order.id,
                _external=True,
            )
            == response.headers["Location"]
        )

    def test_editing_with_invalid_data(self, user_session, client):
        queue_length = len(queue.get_queue())
        user_session(self.portfolio.owner)
        response = self._post(
            client,
            {
                "contracting_officer-phone_number": "invalid input",
                "security_officer-first_name": "Boba",
                "security_officer-last_name": "Fett",
            },
        )

        assert "There were some errors" in response.data.decode()

        updated_task_order = TaskOrders.get(self.task_order.id)
        assert updated_task_order.so_first_name != "Boba"
        assert len(queue.get_queue()) == queue_length
        assert response.status_code == 400

    def test_user_can_only_invite_to_task_order_in_their_portfolio(
        self, user_session, client, portfolio
    ):
        other_task_order = TaskOrderFactory.create()
        user_session(portfolio.owner)

        # user can't see invites
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=portfolio.id,
                task_order_id=other_task_order.id,
            )
        )
        assert response.status_code == 404

        # user can't send invites
        time_updated = other_task_order.time_updated
        response = client.post(
            url_for(
                "portfolios.edit_task_order_invitations",
                portfolio_id=portfolio.id,
                task_order_id=other_task_order.id,
            ),
            data={
                "contracting_officer-first_name": "Luke",
                "contracting_officer-last_name": "Skywalker",
                "contracting_officer-dod_id": "0123456789",
                "contracting_officer-email": "luke@skywalker.mil",
                "contracting_officer-phone_number": "0123456789",
                "contracting_officer-invite": "y",
            },
        )
        assert response.status_code == 404
        assert time_updated == other_task_order.time_updated

        # user can't resend invites
        response = client.post(
            url_for(
                "portfolios.resend_invite",
                portfolio_id=portfolio.id,
                task_order_id=other_task_order.id,
                invite_type="ko_invite",
            )
        )
        assert response.status_code == 404
        assert time_updated == other_task_order.time_updated

    def test_does_not_render_resend_invite_if_user_is_mo_and_user_is_ko(
        self, client, user_session
    ):
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            ko_first_name=self.portfolio.owner.first_name,
            ko_last_name=self.portfolio.owner.last_name,
            ko_email=self.portfolio.owner.email,
            ko_phone_number=self.portfolio.owner.phone_number,
            ko_dod_id=self.portfolio.owner.dod_id,
            ko_invite=True,
        )
        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" not in response.data.decode()

    def test_renders_resend_invite_if_user_is_mo_and_user_is_not_ko(
        self, client, user_session
    ):
        ko = UserFactory.create()
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            contracting_officer=ko,
            ko_invite=True,
        )
        portfolio_role = PortfolioRoleFactory.create(portfolio=self.portfolio, user=ko)
        invitation = InvitationFactory.create(
            inviter=self.portfolio.owner,
            portfolio_role=portfolio_role,
            user=ko,
            status=InvitationStatus.PENDING,
        )

        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" in response.data.decode()

    def test_does_not_render_resend_invite_if_user_is_mo_and_user_is_cor(
        self, client, user_session
    ):
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            cor_first_name=self.portfolio.owner.first_name,
            cor_last_name=self.portfolio.owner.last_name,
            cor_email=self.portfolio.owner.email,
            cor_phone_number=self.portfolio.owner.phone_number,
            cor_dod_id=self.portfolio.owner.dod_id,
            cor_invite=True,
        )
        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" not in response.data.decode()

    def test_renders_resend_invite_if_user_is_mo_and_user_is_not_cor(
        self, client, user_session
    ):
        cor = UserFactory.create()
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            contracting_officer_representative=cor,
            cor_invite=True,
        )
        portfolio_role = PortfolioRoleFactory.create(portfolio=self.portfolio, user=cor)
        invitation = InvitationFactory.create(
            inviter=self.portfolio.owner,
            portfolio_role=portfolio_role,
            user=cor,
            status=InvitationStatus.PENDING,
        )

        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" in response.data.decode()

    def test_does_not_render_resend_invite_if_user_is_mo_and_user_is_so(
        self, client, user_session
    ):
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            so_first_name=self.portfolio.owner.first_name,
            so_last_name=self.portfolio.owner.last_name,
            so_email=self.portfolio.owner.email,
            so_phone_number=self.portfolio.owner.phone_number,
            so_dod_id=self.portfolio.owner.dod_id,
            so_invite=True,
        )
        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" not in response.data.decode()

    def test_renders_resend_invite_if_user_is_mo_and_user_is_not_so(
        self, client, user_session
    ):
        so = UserFactory.create()
        task_order = TaskOrderFactory.create(
            portfolio=self.portfolio,
            creator=self.portfolio.owner,
            security_officer=so,
            so_invite=True,
        )
        portfolio_role = PortfolioRoleFactory.create(portfolio=self.portfolio, user=so)
        invitation = InvitationFactory.create(
            inviter=self.portfolio.owner,
            portfolio_role=portfolio_role,
            user=so,
            status=InvitationStatus.PENDING,
        )

        user_session(self.portfolio.owner)
        response = client.get(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=self.portfolio.id,
                task_order_id=task_order.id,
            )
        )
        assert "Resend Invitation" in response.data.decode()


def test_ko_can_view_task_order(client, user_session, portfolio, user):
    PortfolioRoleFactory.create(
        portfolio=portfolio,
        user=user,
        status=PortfolioStatus.ACTIVE,
        permission_sets=[
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO),
            PermissionSets.get(PermissionSets.VIEW_PORTFOLIO_FUNDING),
        ],
    )
    task_order = TaskOrderFactory.create(portfolio=portfolio, contracting_officer=user)
    user_session(user)

    response = client.get(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200
    assert translate("common.manage") in response.data.decode()

    TaskOrders.update(task_order, clin_01=None)
    response = client.get(
        url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200
    assert translate("common.manage") not in response.data.decode()


def test_can_view_task_order_invitations_when_complete(client, user_session, portfolio):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    response = client.get(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 200


def test_cant_view_task_order_invitations_when_not_complete(
    client, user_session, portfolio
):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, clin_01=None)
    response = client.get(
        url_for(
            "portfolios.task_order_invitations",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 404


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
    request_url = url_for(
        "portfolios.ko_review", portfolio_id=portfolio.id, task_order_id=task_order.id
    )

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
    response = client.get(
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert response.status_code == 404


def test_mo_redirected_to_build_page(client, user_session, portfolio):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)

    response = client.get(
        url_for("task_orders.new", screen=1, task_order_id=task_order.id)
    )
    assert response.status_code == 200


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
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=form_data,
    )

    assert task_order.pdf
    assert response.headers["Location"] == url_for(
        "portfolios.view_task_order",
        task_order_id=task_order.id,
        portfolio_id=portfolio.id,
        _external=True,
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
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=form_data,
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
        url_for(
            "portfolios.ko_review",
            portfolio_id=portfolio.id,
            task_order_id=other_task_order.id,
        )
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
        url_for(
            "portfolios.submit_ko_review",
            portfolio_id=portfolio.id,
            task_order_id=other_task_order.id,
        ),
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
        url_for(
            "portfolios.so_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
    )
    assert owner_response.status_code == 404

    with captured_templates(app) as templates:
        user_session(so)
        so_response = app.test_client().get(
            url_for(
                "portfolios.so_review",
                portfolio_id=portfolio.id,
                task_order_id=task_order.id,
            )
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
        url_for(
            "portfolios.submit_so_review",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        ),
        data=dd_254_data,
    )
    expected_redirect = url_for(
        "portfolios.view_task_order",
        portfolio_id=portfolio.id,
        task_order_id=task_order.id,
        _external=True,
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
        url_for(
            "portfolios.so_review",
            portfolio_id=portfolio.id,
            task_order_id=other_task_order.id,
        )
    )
    assert response.status_code == 404

    # SO can't submit dd254
    response = client.post(
        url_for(
            "portfolios.submit_so_review",
            portfolio_id=portfolio.id,
            task_order_id=other_task_order.id,
        ),
        data=dd_254_data,
    )
    assert response.status_code == 404
    assert not other_task_order.dd_254


def test_resend_invite_when_invalid_invite_officer(
    app, client, user_session, portfolio, user
):
    queue_length = len(queue.get_queue())

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=user, ko_invite=True
    )

    PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioStatus.ACTIVE
    )

    user_session(user)

    response = client.post(
        url_for(
            "portfolios.resend_invite",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
            _external=True,
        ),
        data={"invite_type": "invalid_invite_type"},
    )

    assert response.status_code == 404
    assert len(queue.get_queue()) == queue_length


def test_resend_invite_when_officer_type_missing(
    app, client, user_session, portfolio, user
):
    queue_length = len(queue.get_queue())

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=None, ko_invite=True
    )

    PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioStatus.ACTIVE
    )

    user_session(user)

    response = client.post(
        url_for(
            "portfolios.resend_invite",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
            _external=True,
        ),
        data={"invite_type": "contracting_officer_invite"},
    )

    assert response.status_code == 404
    assert len(queue.get_queue()) == queue_length


def test_resend_invite_when_not_pending(app, client, user_session, portfolio, user):
    queue_length = len(queue.get_queue())

    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=user, ko_invite=True
    )

    portfolio_role = PortfolioRoleFactory.create(
        portfolio=portfolio, user=user, status=PortfolioStatus.ACTIVE
    )

    original_invitation = InvitationFactory.create(
        inviter=user,
        portfolio_role=portfolio_role,
        email=user.email,
        status=InvitationStatus.ACCEPTED,
    )

    user_session(user)

    response = client.post(
        url_for(
            "portfolios.resend_invite",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
            _external=True,
        ),
        data={"invite_type": "ko_invite"},
    )

    assert original_invitation.status == InvitationStatus.ACCEPTED
    assert response.status_code == 404
    assert len(queue.get_queue()) == queue_length


def test_resending_revoked_invite(app, client, user_session, portfolio, user):
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=user, ko_invite=True
    )

    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=user)

    invite = InvitationFactory.create(
        inviter=user,
        portfolio_role=portfolio_role,
        email=user.email,
        status=InvitationStatus.REVOKED,
    )

    user_session(user)

    response = client.post(
        url_for(
            "portfolios.resend_invite",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
            invite_type="ko_invite",
            _external=True,
        )
    )

    assert invite.is_revoked
    assert response.status_code == 404


def test_resending_expired_invite(app, client, user_session, portfolio):
    queue_length = len(queue.get_queue())

    ko = UserFactory.create()
    task_order = TaskOrderFactory.create(
        portfolio=portfolio, contracting_officer=ko, ko_invite=True
    )
    portfolio_role = PortfolioRoleFactory.create(portfolio=portfolio, user=ko)
    invite = InvitationFactory.create(
        inviter=portfolio.owner,
        portfolio_role=portfolio_role,
        email=ko.email,
        expiration_time=datetime.now() - timedelta(days=1),
    )
    user_session(portfolio.owner)

    response = client.post(
        url_for(
            "portfolios.resend_invite",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
            invite_type="ko_invite",
            _external=True,
        )
    )

    assert invite.is_expired
    assert response.status_code == 302
    assert len(queue.get_queue()) == queue_length + 1
