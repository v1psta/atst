import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.pe_numbers import PENumbers

from tests.factories import PENumberFactory


@pytest.fixture(scope="function")
def new_pe_number(session):
    def make_pe_number(**kwargs):
        pen = PENumberFactory.create(**kwargs)
        session.add(pen)
        session.commit()

        return pen

    return make_pe_number


def test_can_get_pe_number(new_pe_number):
    new_pen = new_pe_number(number="0701367F", description="Combat Support - Offensive")
    pen = PENumbers.get(new_pen.number)

    assert pen.number == new_pen.number


def test_nonexistent_pe_number_raises():
    with pytest.raises(NotFoundError):
        PENumbers.get("some fake number")

def test_create_many():
    pen_list = [['123456', 'Land Speeder'], ['7891011', 'Lightsaber']]
    PENumbers.create_many(pen_list)

    assert PENumbers.get(pen_list[0][0])
    assert PENumbers.get(pen_list[1][0])
