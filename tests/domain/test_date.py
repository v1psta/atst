import pytest
import pendulum

from atst.domain.date import parse_date


def test_date_with_slashes():
    date_str = "1/2/2020"
    assert parse_date(date_str) == pendulum.date(2020, 1, 2)


def test_date_with_dashes():
    date_str = "2020-1-2"
    assert parse_date(date_str) == pendulum.date(2020, 1, 2)


def test_invalid_date():
    date_str = "This is not a valid data"
    with pytest.raises(ValueError):
        parse_date(date_str)

