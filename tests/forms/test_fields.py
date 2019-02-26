import pytest
from wtforms import Form
from wtforms.fields import StringField
import pendulum
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.fields import FormFieldWrapper


class PersonForm(Form):
    first_name = StringField("first_name")


class FormWithFormField(Form):
    person = FormFieldWrapper(PersonForm)


class TestFormFieldWrapper:
    class Foo:
        person = {"first_name": "Luke"}

    obj = Foo()

    def test_form_data_does_not_match_object_data(self):
        form_data = ImmutableMultiDict({"person-first_name": "Han"})
        form = FormWithFormField(form_data, obj=self.obj)
        assert form.person.has_changes()

    def test_when_no_form_data(self):
        form = FormWithFormField(None, obj=self.obj)
        assert not form.person.has_changes()

    def test_when_no_obj_data(self):
        form_data = ImmutableMultiDict({"person-first_name": "Han"})
        form = FormWithFormField(form_data)
        assert not form.person.has_changes()

    def test_when_form_data_matches_obj_dta(self):
        form_data = ImmutableMultiDict({"person-first_name": "Luke"})
        form = FormWithFormField(form_data, obj=self.obj)
        assert not form.person.has_changes()
