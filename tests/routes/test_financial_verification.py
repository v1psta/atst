import pytest
from unittest.mock import MagicMock
from flask import url_for

from atst.eda_client import MockEDAClient
from atst.routes.requests.financial_verification import (
    UpdateFinancialVerification,
    SaveFinancialVerificationDraft,
)

from tests.mocks import MOCK_REQUEST, MOCK_USER, MOCK_VALID_PE_ID
from tests.factories import (
    PENumberFactory,
    RequestFactory,
    UserFactory,
    RequestStatusEventFactory,
    RequestReviewFactory,
)
from atst.forms.exceptions import FormValidationError
from atst.domain.requests.financial_verification import (
    PENumberValidator,
    TaskOrderNumberValidator,
)


@pytest.fixture
def fv_data():
    return {
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


TrueValidator = MagicMock()
TrueValidator.validate = MagicMock(return_value=True)

FalseValidator = MagicMock()
FalseValidator.validate = MagicMock(return_value=False)


def test_update_fv(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "pe_id": MOCK_VALID_PE_ID}

    updated_request = UpdateFinancialVerification(
        TrueValidator, TrueValidator, user, request, data, is_extended=False
    ).execute()

    assert updated_request.is_pending_ccpo_approval



def test_update_fv_re_enter_pe_number(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "pe_id": "0101228M"}
    update_fv = UpdateFinancialVerification(
        PENumberValidator(), TrueValidator, user, request, data, is_extended=False
    )

    with pytest.raises(FormValidationError):
        update_fv.execute()
    updated_request = update_fv.execute()

    assert updated_request.is_pending_ccpo_approval


def test_update_fv_invalid_task_order_number(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "task_order_number": "DCA10096D0051"}
    update_fv = UpdateFinancialVerification(
        TrueValidator,
        TaskOrderNumberValidator(),
        user,
        request,
        data,
        is_extended=False,
    )

    with pytest.raises(FormValidationError):
        update_fv.execute()


def test_update_fv_extended(fv_data, extended_financial_verification_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, **extended_financial_verification_data}
    update_fv = UpdateFinancialVerification(
        TrueValidator, TaskOrderNumberValidator(), user, request, data, is_extended=True
    )

    assert update_fv.execute()


def test_update_fv_missing_extended_data(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    update_fv = UpdateFinancialVerification(
        TrueValidator,
        TaskOrderNumberValidator(),
        user,
        request,
        fv_data,
        is_extended=True,
    )

    with pytest.raises(FormValidationError):
        update_fv.execute()


def test_update_fv_submission(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    updated_request = UpdateFinancialVerification(
        TrueValidator, TrueValidator, user, request, fv_data
    ).execute()
    assert updated_request


def test_save_empty_draft():
    request = RequestFactory.create()
    user = UserFactory.create()
    save_draft = SaveFinancialVerificationDraft(
        TrueValidator, TrueValidator, user, request, {}, is_extended=False
    )

    assert save_draft.execute()


def test_save_draft_with_ba_code():
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {"ba_code": "02A"}
    save_draft = SaveFinancialVerificationDraft(
        TrueValidator, TrueValidator, user, request, data, is_extended=False
    )

    assert save_draft.execute()


def test_save_draft_with_invalid_task_order(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    save_draft = SaveFinancialVerificationDraft(
        TrueValidator, FalseValidator, user, request, fv_data, is_extended=False
    )

    with pytest.raises(FormValidationError):
        assert save_draft.execute()


def test_save_draft_with_invalid_pe_number(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    save_draft = SaveFinancialVerificationDraft(
        FalseValidator, TrueValidator, user, request, fv_data, is_extended=False
    )

    with pytest.raises(FormValidationError):
        assert save_draft.execute()


def test_save_draft_re_enter_pe_number(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "pe_id": "0101228M"}
    save_fv = SaveFinancialVerificationDraft(
        PENumberValidator(), TrueValidator, user, request, data, is_extended=False
    )

    with pytest.raises(FormValidationError):
        save_fv.execute()
    save_fv.execute()


def test_update_fv_route(client, user_session, fv_data):
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    user_session(user)
    response = client.post(
        url_for("requests.financial_verification", request_id=request.id),
        data=fv_data,
        follow_redirects=False,
    )

    assert response.status_code == 200


def test_save_fv_draft_route(client, user_session, fv_data):
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    user_session(user)
    response = client.post(
        url_for("requests.save_financial_verification_draft", request_id=request.id),
        data=fv_data,
        follow_redirects=False,
    )

    assert response.status_code == 200


def test_get_fv_form_route(client, user_session, fv_data):
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)
    user_session(user)
    response = client.get(
        url_for("requests.financial_verification", request_id=request.id),
        data=fv_data,
        follow_redirects=False,
    )

    assert response.status_code == 200
