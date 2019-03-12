import pytest
from wtforms.fields import RadioField
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.forms import BaseForm


class FormWithChoices(BaseForm):
    force_side = RadioField(
        "Choose your side",
        choices=[
            ("light", "Light Side"),
            ("dark", "Dark Side"),
            ("neutral", "Chaotic Neutral"),
        ],
    )


class TestBaseForm:
    class Foo:
        person = {"force_side": None}

    obj = Foo()

    def test_radio_field_saves_only_as_choice(self):
        form_data_1 = ImmutableMultiDict({"force_side": "None"})
        form_1 = FormWithChoices(form_data_1, obj=self.obj)
        assert form_1.data["force_side"] is None

        form_data_2 = ImmutableMultiDict({"force_side": "a fake choice"})
        form_2 = FormWithChoices(form_data_2, obj=self.obj)
        assert form_2.data["force_side"] is None

        form_data_3 = ImmutableMultiDict({"force_side": "dark"})
        form_3 = FormWithChoices(form_data_3, obj=self.obj)
        assert form_3.data["force_side"] is "dark"
