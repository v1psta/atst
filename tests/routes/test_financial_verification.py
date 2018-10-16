import pytest
from unittest.mock import MagicMock

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


class MockPEValidator(object):
    def validate(self, request, field):
        return True


class MockTaskOrderValidator(object):
    def validate(self, field):
        return True


def test_update(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "pe_id": MOCK_VALID_PE_ID}

    response_context = UpdateFinancialVerification(
        TrueValidator, TrueValidator, user, request, data, is_extended=False
    ).execute()

    assert response_context.get("workspace")


def test_re_enter_pe_number(fv_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, "pe_id": "0101228M"}
    update_fv = UpdateFinancialVerification(
        PENumberValidator(), TrueValidator, user, request, data, is_extended=False
    )

    with pytest.raises(FormValidationError):
        update_fv.execute()
    response_context = update_fv.execute()

    assert response_context.get("status", "submitted")


def test_invalid_task_order_number(fv_data):
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


def test_extended_fv_data(fv_data, extended_financial_verification_data):
    request = RequestFactory.create()
    user = UserFactory.create()
    data = {**fv_data, **extended_financial_verification_data}
    update_fv = UpdateFinancialVerification(
        TrueValidator, TaskOrderNumberValidator(), user, request, data, is_extended=True
    )

    assert update_fv.execute()


def test_missing_extended_fv_data(fv_data):
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

    response_context = save_draft.execute()
    request = response_context["request"]


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
