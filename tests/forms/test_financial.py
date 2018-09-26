import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.financial import suggest_pe_id, FinancialForm, ExtendedFinancialForm
from atst.eda_client import MockEDAClient


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
    assert suggest_pe_id(input_) == expected


def test_funding_type_other_not_required_if_funding_type_is_not_other():
    form_data = {"funding_type": "PROC"}
    form = ExtendedFinancialForm(data=form_data)
    form.validate()
    assert "funding_type_other" not in form.errors


def test_funding_type_other_required_if_funding_type_is_other():
    form_data = {"funding_type": "OTHER"}
    form = ExtendedFinancialForm(data=form_data)
    form.validate()
    assert "funding_type_other" in form.errors


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
    form_data = {"treasury_code": input_}
    form = FinancialForm(data=form_data)
    form.validate()
    is_valid = "treasury_code" not in form.errors

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
    form_data = ImmutableMultiDict([("ba_code", input_)])
    form = FinancialForm(form_data)
    form.validate()
    is_valid = "ba_code" not in form.errors

    assert is_valid == expected


def test_task_order_number_validation(monkeypatch):
    monkeypatch.setattr(
        "atst.domain.task_orders.TaskOrders._client", lambda: MockEDAClient()
    )
    monkeypatch.setattr("atst.forms.financial.validate_pe_id", lambda *args: True)
    form_invalid = FinancialForm(data={"task_order_number": "1234"})
    form_invalid.perform_extra_validation({})

    assert "task_order_number" in form_invalid.errors

    form_valid = FinancialForm(
        data={"task_order_number": MockEDAClient.MOCK_CONTRACT_NUMBER},
        eda_client=MockEDAClient(),
    )
    form_valid.perform_extra_validation({})

    assert "task_order_number" not in form_valid.errors


def test_can_submit_zero_for_clin():
    form_first = ExtendedFinancialForm()
    form_first.validate()
    assert "clin_0001" in form_first.errors
    form_data = ImmutableMultiDict([("clin_0001", "0")])
    form_second = ExtendedFinancialForm(form_data)
    form_second.validate()
    assert "clin_0001" not in form_second.errors
