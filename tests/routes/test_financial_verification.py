import urllib
import pytest
from flask import url_for

from atst.eda_client import MockEDAClient
from atst.models.request_status_event import RequestStatus
from atst.routes.requests.financial_verification import FinancialVerification

from tests.mocks import MOCK_REQUEST, MOCK_USER
from tests.factories import (
    PENumberFactory,
    RequestFactory,
    UserFactory,
    RequestStatusEventFactory,
    RequestReviewFactory,
)


class TestPENumberInForm:

    required_data = {
        "pe_id": "123",
        "task_order_number": MockEDAClient.MOCK_CONTRACT_NUMBER,
        "fname_co": "Contracting",
        "lname_co": "Officer",
        "email_co": "jane@mail.mil",
        "office_co": "WHS",
        "fname_cor": "Officer",
        "lname_cor": "Representative",
        "email_cor": "jane@mail.mil",
        "office_cor": "WHS",
        "uii_ids": "1234",
        "treasury_code": "00123456",
        "ba_code": "02A",
    }

    def _set_monkeypatches(self, monkeypatch):
        monkeypatch.setattr(
            "atst.forms.financial.FinancialForm.validate", lambda s: True
        )
        user = UserFactory.create()
        monkeypatch.setattr("atst.domain.auth.get_current_user", lambda *args: user)
        return user

    def submit_data(self, client, user, data, extended=False):
        request = RequestFactory.create(creator=user)
        url_kwargs = {"request_id": request.id}
        if extended:
            url_kwargs["extended"] = True
        response = client.post(
            url_for("requests.financial_verification", **url_kwargs),
            data=data,
            follow_redirects=False,
        )
        return response

    def test_submit_request_form_with_invalid_pe_id(self, monkeypatch, client):
        user = self._set_monkeypatches(monkeypatch)

        response = self.submit_data(client, user, self.required_data)

        assert "We couldn&#39;t find that PE number" in response.data.decode()
        assert response.status_code == 200

    def test_submit_request_form_with_unchanged_pe_id(self, monkeypatch, client):
        user = self._set_monkeypatches(monkeypatch)

        data = dict(self.required_data)
        data["pe_id"] = "0101110F"

        response = self.submit_data(client, user, data)

        assert response.status_code == 302
        assert "/workspaces" in response.headers.get("Location")

    def test_submit_request_form_with_new_valid_pe_id(self, monkeypatch, client):
        user = self._set_monkeypatches(monkeypatch)
        pe = PENumberFactory.create(number="8675309U", description="sample PE number")

        data = dict(self.required_data)
        data["pe_id"] = pe.number

        response = self.submit_data(client, user, data)

        assert response.status_code == 302
        assert "/workspaces" in response.headers.get("Location")

    def test_submit_request_form_with_missing_pe_id(self, monkeypatch, client):
        user = self._set_monkeypatches(monkeypatch)

        data = dict(self.required_data)
        data["pe_id"] = ""

        response = self.submit_data(client, user, data)

        assert "There were some errors" in response.data.decode()
        assert response.status_code == 200

    def test_submit_financial_form_with_invalid_task_order(
        self, monkeypatch, user_session, client
    ):
        user = UserFactory.create()
        user_session(user)

        data = dict(self.required_data)
        data["pe_id"] = "0101110F"
        data["task_order_number"] = "1234"

        response = self.submit_data(client, user, data)

        assert "extended=True" in response.data.decode()

    def test_submit_financial_form_with_valid_task_order(
        self, monkeypatch, user_session, client
    ):
        user = UserFactory.create()
        monkeypatch.setattr(
            "atst.domain.requests.Requests.get", lambda *args: MOCK_REQUEST
        )
        user_session(user)

        data = dict(self.required_data)
        data["pe_id"] = "0101110F"
        data["task_order_number"] = MockEDAClient.MOCK_CONTRACT_NUMBER

        response = self.submit_data(client, user, data)

        assert "enter TO information manually" not in response.data.decode()

    def test_submit_extended_financial_form(
        self, monkeypatch, user_session, client, extended_financial_verification_data
    ):
        user = UserFactory.create()
        request = RequestFactory.create(creator=user)
        monkeypatch.setattr("atst.domain.requests.Requests.get", lambda *args: request)
        monkeypatch.setattr("atst.forms.financial.validate_pe_id", lambda *args: True)
        user_session(user)
        data = {**self.required_data, **extended_financial_verification_data}
        data["task_order_number"] = "1234567"

        response = self.submit_data(client, user, data, extended=True)

        assert response.status_code == 302
        assert "/requests" in response.headers.get("Location")

    def test_submit_invalid_extended_financial_form(
        self, monkeypatch, user_session, client, extended_financial_verification_data
    ):
        monkeypatch.setattr("atst.forms.financial.validate_pe_id", lambda *args: True)
        user = UserFactory.create()
        user_session(user)
        data = {**self.required_data, **extended_financial_verification_data}
        data["task_order_number"] = "1234567"
        del (data["clin_0001"])

        response = self.submit_data(client, user, data, extended=True)

        assert response.status_code == 200


def test_displays_ccpo_review_comment(user_session, client):
    creator = UserFactory.create()
    ccpo = UserFactory.from_atat_role("ccpo")
    user_session(creator)
    request = RequestFactory.create(creator=creator)
    status = RequestStatusEventFactory.create(
        revision=request.latest_revision,
        new_status=RequestStatus.CHANGES_REQUESTED_TO_FINVER,
        request=request,
    )
    review_comment = "add all of the correct info, instead of the incorrect info"
    RequestReviewFactory.create(reviewer=ccpo, comment=review_comment, status=status)
    response = client.get("/requests/verify/{}".format(request.id))
    body = response.data.decode()
    assert review_comment in body


class TestFinancialVerification:
    @pytest.fixture(scope="function", autouse=True)
    def apply_monkeypath(self, monkeypatch):
        monkeypatch.setattr(
            "atst.domain.requests.Requests.get", lambda *args: self.request
        )

    def _service_object(self, request=None, extended=False, post_data={}):
        if not request:
            self.request = RequestFactory.create()
        else:
            self.request = request

        return FinancialVerification(
            UserFactory.create(),
            self.request.id,
            extended=extended,
            post_data=post_data,
        )

    def test_is_extended(self):
        finver_one = self._service_object()
        assert not finver_one.is_extended
        finver_two = self._service_object(
            request=RequestFactory.create_with_status(
                RequestStatus.CHANGES_REQUESTED_TO_FINVER
            )
        )
        assert finver_two.is_extended
        finver_three = self._service_object(extended=True)
        assert finver_three.is_extended
