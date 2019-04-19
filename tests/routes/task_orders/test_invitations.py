from datetime import datetime, timedelta

from flask import url_for
import pytest

from atst.domain.task_orders import TaskOrders
from atst.models.invitation import Status as InvitationStatus
from atst.models.portfolio_role import Status as PortfolioStatus
from atst.queue import queue

from tests.factories import (
    PortfolioFactory,
    TaskOrderFactory,
    UserFactory,
    PortfolioRoleFactory,
    InvitationFactory,
)


def test_invite(client, user_session):
    portfolio = PortfolioFactory.create()
    user_session(portfolio.owner)
    to = TaskOrderFactory.create(portfolio=portfolio)
    response = client.post(
        url_for("task_orders.invite", task_order_id=to.id), follow_redirects=False
    )
    redirect = url_for("task_orders.view_task_order", task_order_id=to.id)
    assert redirect in response.headers["Location"]


def test_invite_officers_to_task_order(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        ko_invite=True, cor_invite=True, so_invite=True
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    # owner and three officers are portfolio members
    assert len(portfolio.members) == 4
    # email invitations are enqueued
    assert len(queue.get_queue()) == 3
    # task order has relationship to user for each officer role
    assert task_order.contracting_officer.dod_id == task_order.ko_dod_id
    assert task_order.contracting_officer_representative.dod_id == task_order.cor_dod_id
    assert task_order.security_officer.dod_id == task_order.so_dod_id


def test_add_officer_but_do_not_invite(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        ko_invite=False, cor_invite=False, so_invite=False
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    portfolio = task_order.portfolio
    # owner is only portfolio member
    assert len(portfolio.members) == 1
    # no invitations are enqueued
    assert len(queue.get_queue()) == 0


def test_does_not_resend_officer_invitation(client, user_session):
    user = UserFactory.create()
    contracting_officer = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    task_order = TaskOrderFactory.create(
        creator=user,
        portfolio=portfolio,
        ko_first_name=contracting_officer.first_name,
        ko_last_name=contracting_officer.last_name,
        ko_dod_id=contracting_officer.dod_id,
        ko_invite=True,
    )

    user_session(user)
    for i in range(2):
        client.post(url_for("task_orders.invite", task_order_id=task_order.id))
    assert len(contracting_officer.invitations) == 1


def test_does_not_invite_if_task_order_incomplete(client, user_session, queue):
    task_order = TaskOrderFactory.create(
        scope=None, ko_invite=True, cor_invite=True, so_invite=True
    )
    portfolio = task_order.portfolio

    user_session(portfolio.owner)
    response = client.post(url_for("task_orders.invite", task_order_id=task_order.id))

    # redirected to review screen
    assert response.headers["Location"] == url_for(
        "task_orders.new", screen=4, task_order_id=task_order.id, _external=True
    )
    # only owner is portfolio member
    assert len(portfolio.members) == 1
    # no email invitations are enqueued
    assert len(queue.get_queue()) == 0


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


class TestTaskOrderInvitations:
    def setup(self):
        self.portfolio = PortfolioFactory.create()
        self.task_order = TaskOrderFactory.create(portfolio=self.portfolio)

    def _post(self, client, updates):
        return client.post(
            url_for("task_orders.invitations_edit", task_order_id=self.task_order.id),
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
                "task_orders.invitations",
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
                "task_orders.invitations",
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
            url_for("task_orders.invitations", task_order_id=other_task_order.id)
        )
        assert response.status_code == 404

        # user can't send invites
        time_updated = other_task_order.time_updated
        response = client.post(
            url_for("task_orders.invitations_edit", task_order_id=other_task_order.id),
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
                "task_orders.resend_invite",
                task_order_id=other_task_order.id,
                invite_type="ko_invite",
            )
        )
        assert response.status_code == 404
        assert time_updated == other_task_order.time_updated

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
            url_for("task_orders.invitations", task_order_id=task_order.id)
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
            url_for("task_orders.invitations", task_order_id=task_order.id)
        )
        assert "Resend Invitation" in response.data.decode()


def test_can_view_task_order_invitations_when_complete(client, user_session, portfolio):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    response = client.get(
        url_for("task_orders.invitations", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_cant_view_task_order_invitations_when_not_complete(
    client, user_session, portfolio
):
    user_session(portfolio.owner)
    task_order = TaskOrderFactory.create(portfolio=portfolio, clin_01=None)
    response = client.get(
        url_for("task_orders.invitations", task_order_id=task_order.id)
    )
    assert response.status_code == 404


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
            "task_orders.resend_invite", task_order_id=task_order.id, _external=True
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
            "task_orders.resend_invite", task_order_id=task_order.id, _external=True
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
            "task_orders.resend_invite", task_order_id=task_order.id, _external=True
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
            "task_orders.resend_invite",
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
            "task_orders.resend_invite",
            task_order_id=task_order.id,
            invite_type="ko_invite",
            _external=True,
        )
    )

    assert invite.is_expired
    assert response.status_code == 302
    assert len(queue.get_queue()) == queue_length + 1
