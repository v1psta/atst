import pytest
from wtforms import Form
import pendulum
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.fields import NewlineListField


class NewlineListForm(Form):
    newline_list = NewlineListField()


@pytest.mark.parametrize(
    "input_,expected",
    [
        ("", []),
        ("hello", ["hello"]),
        ("hello\n", ["hello"]),
        ("hello\nworld", ["hello", "world"]),
        ("hello\nworld\n", ["hello", "world"]),
    ],
)
def test_newline_list_process(input_, expected):
    form_data = ImmutableMultiDict({"newline_list": input_})
    form = NewlineListForm(form_data)

    assert form.validate()
    assert form.data == {"newline_list": expected}


@pytest.mark.parametrize(
    "input_,expected",
    [([], ""), (["hello"], "hello"), (["hello", "world"], "hello\nworld")],
)
def test_newline_list_value(input_, expected):
    form_data = {"newline_list": input_}
    form = NewlineListForm(data=form_data)

    assert form.validate()
    assert form.newline_list._value() == expected
