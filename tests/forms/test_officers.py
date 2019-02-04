from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.officers import EditTaskOrderOfficersForm
from tests.factories import TaskOrderFactory, UserFactory


class TestEditTaskOrderOfficersForm:
    def _assert_officer_info_matches(self, form, task_order, officer):
        prefix = form.OFFICER_PREFIXES[officer]

        for field in form.OFFICER_INFO_FIELD_NAMES:
            assert form[officer][field].data == getattr(
                task_order, "{}_{}".format(prefix, field)
            )

    def test_processing_with_existing_task_order(self):
        task_order = TaskOrderFactory.create()
        form = EditTaskOrderOfficersForm(obj=task_order)
        for officer in form.OFFICER_PREFIXES.keys():
            self._assert_officer_info_matches(form, task_order, officer)

    def test_processing_form_with_formdata(self):
        data = {
            "contracting_officer-first_name": "Han",
            "contracting_officer-last_name": "Solo",
        }
        formdata = ImmutableMultiDict(data)
        task_order = TaskOrderFactory.create()
        form = EditTaskOrderOfficersForm(formdata=formdata, obj=task_order)

        for officer in ["contracting_officer_representative", "security_officer"]:
            self._assert_officer_info_matches(form, task_order, officer)

        prefix = "ko"
        officer = "contracting_officer"
        for field in form.OFFICER_INFO_FIELD_NAMES:
            data_field = "{}-{}".format(officer, field)
            if data_field in formdata:
                assert form[officer][field].data == formdata[data_field]
            else:
                assert form[officer][field].data == getattr(
                    task_order, "{}_{}".format(prefix, field)
                )

    def test_populate_obj(self):
        data = {
            "security_officer-first_name": "Luke",
            "security_officer-last_name": "Skywalker",
        }
        formdata = ImmutableMultiDict(data)
        task_order = TaskOrderFactory.create()
        form = EditTaskOrderOfficersForm(formdata=formdata, obj=task_order)

        form.populate_obj(task_order)
        assert task_order.so_first_name == data["security_officer-first_name"]
        assert task_order.so_last_name == data["security_officer-last_name"]

    def test_email_validation(self):
        data = {"contracting_officer-email": "not_really_an_email_address"}
        formdata = ImmutableMultiDict(data)
        form = EditTaskOrderOfficersForm(formdata)
        assert not form.validate()
        assert form.contracting_officer.email.errors == ["Invalid email address."]
