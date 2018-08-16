import pytest

from atst.forms.financial import suggest_pe_id, FinancialForm


@pytest.mark.parametrize("input_,expected", [
    ('0603502N', None),
    ('0603502NZ', None),
    ('603502N', '0603502N'),
    ('063502N', '0603502N'),
    ('63502N', '0603502N'),
])
def test_suggest_pe_id(input_, expected):
    assert suggest_pe_id(input_) == expected


def test_funding_type_other_not_required_if_funding_type_is_not_other():
    form_data = {
        "funding_type": "PROC"
    }
    form = FinancialForm(data=form_data)
    form.validate()
    assert "funding_type_other" not in form.errors


def test_funding_type_other_required_if_funding_type_is_other():
    form_data = {
        "funding_type": "OTHER"
    }
    form = FinancialForm(data=form_data)
    form.validate()
    assert "funding_type_other" in form.errors
