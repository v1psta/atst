import pytest
from wtforms import Form
import pendulum

from atst.forms.fields import DateField


class MyForm(Form):
    date = DateField()


def test_date_ie_format():
    form = MyForm(data={"date": "12/24/2018"})
    assert form.date._value() == pendulum.date(2018, 12, 24)


def test_date_sane_format():
    form = MyForm(data={"date": "2018-12-24"})
    assert form.date._value() == pendulum.date(2018, 12, 24)


def test_date_insane_format():
    form = MyForm(data={"date": "hello"})
    with pytest.raises(ValueError):
        form.date._value()
