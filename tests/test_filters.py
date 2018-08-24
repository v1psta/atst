import pytest

from atst.filters import dollars


@pytest.mark.parametrize(
    "input,expected",
    [
        ("0", "$0"),
        ("123.00", "$123"),
        ("1234567", "$1,234,567"),
        ("-1234", "$-1,234"),
        ("one", "$0"),
    ],
)
def test_dollar_fomatter(input, expected):
    assert dollars(input) == expected
