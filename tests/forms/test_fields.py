import pytest
from uuid import uuid4
from wtforms import Form
from wtforms.fields import StringField
import pendulum
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.fields import FormFieldWrapper, EncryptedHiddenField
from atst.utils.encryption import encrypt_value, decrypt_value


class PersonForm(Form):
    first_name = StringField("first_name")


class FormWithFormField(Form):
    person = FormFieldWrapper(PersonForm)
    uuid = EncryptedHiddenField()


class TestFormFieldWrapper:
    class Foo:
        uuid = uuid4()
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

    def test_when_form_data_matches_obj_data(self):
        form_data = ImmutableMultiDict(
            {"person-first_name": "Luke", "uuid": self.obj.uuid}
        )
        form = FormWithFormField(form_data, obj=self.obj)
        assert not form.person.has_changes()


@pytest.fixture
def encryption_enabled_app(app):
    app.config.update({"ENCRYPT_HIDDEN_FIELDS": True})
    yield app
    app.config.update({"ENCRYPT_HIDDEN_FIELDS": False})


class TestEncryptedHiddenField:
    class Foo:
        uuid = uuid4()
        person = {"first_name": "Luke"}

    obj = Foo()

    def test_encrypt_value(self, encryption_enabled_app):
        assert self.obj.uuid != encrypt_value(self.obj.uuid)

    def test_decrypt_value(self, encryption_enabled_app):
        encrypted_value = encrypt_value(self.obj.uuid)
        assert str(self.obj.uuid) == decrypt_value(encrypted_value)

    def test_process_data(self, encryption_enabled_app):
        form = FormWithFormField(None, obj=self.obj)
        assert self.obj.uuid != form.uuid.data

    def test_process_formdata(self, encryption_enabled_app):
        form = FormWithFormField(None, obj=self.obj)
        EncryptedHiddenField.process_formdata(form.uuid, [form.uuid.data])
        assert str(self.obj.uuid) == form.uuid.data
