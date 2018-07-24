import pytest

from atst.forms.financial import suggest_pe_id


@pytest.mark.parametrize("input,expected", [
    ('0603502N', None),
    ('0603502NZ', None),
    ('603502N', '0603502N'),
    ('063502N', '0603502N'),
    ('63502N', '0603502N'),
])
def test_suggest_pe_id(input, expected):
    assert suggest_pe_id(input) == expected
