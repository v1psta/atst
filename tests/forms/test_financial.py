import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.financial import FinancialVerificationForm
from atst.domain.requests.financial_verification import PENumberValidator


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("0603502N", None),
        ("0603502NZ", None),
        ("603502N", "0603502N"),
        ("063502N", "0603502N"),
        ("63502N", "0603502N"),
    ],
)
def test_suggest_pe_id(input_, expected):
    assert PENumberValidator().suggest_pe_id(input_) == expected


def test_funding_type_other_not_required_if_funding_type_is_not_other():
    form_data = ImmutableMultiDict({"legacy_task_order-funding_type": "PROC"})
    form = FinancialVerificationForm(form_data)
    form.validate()
    assert "funding_type_other" not in form.errors


def test_funding_type_other_required_if_funding_type_is_other():
    form_data = ImmutableMultiDict({"legacy_task_order-funding_type": "OTHER"})
    form = FinancialVerificationForm(form_data)
    form.validate()
    assert "funding_type_other" in form.errors["legacy_task_order"]


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("1234", True),
        ("123456", True),
        ("0001234", True),
        ("000123456", True),
        ("12345", False),
        ("00012345", False),
        ("0001234567", False),
        ("000000", False),
    ],
)
def test_treasury_code_validation(input_, expected):
    form_data = ImmutableMultiDict([("request-treasury_code", input_)])
    form = FinancialVerificationForm(form_data)
    form.validate()
    is_valid = "treasury_code" not in form.errors["request"]

    assert is_valid == expected


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("1", False),
        ("12", True),
        ("01", True),
        ("0A", False),
        ("A", False),
        ("AB", False),
        ("123", True),
        ("012", True),
        ("12A", True),
        ("02A", True),
        ("0012", False),
        ("012A", False),
        ("2AB", False),
    ],
)
def test_ba_code_validation(input_, expected):
    form_data = ImmutableMultiDict([("request-ba_code", input_)])
    form = FinancialVerificationForm(form_data)
    form.validate()
    is_valid = "ba_code" not in form.errors["request"]

    assert is_valid == expected


def test_can_submit_zero_for_clin():
    form_first = FinancialVerificationForm()
    form_first.validate()
    assert "clin_0001" in form_first.errors["legacy_task_order"]
    form_data = ImmutableMultiDict([("legacy_task_order-clin_0001", "0")])
    form_second = FinancialVerificationForm(form_data)
    form_second.validate()
    assert "clin_0001" not in form_second.errors["legacy_task_order"]
