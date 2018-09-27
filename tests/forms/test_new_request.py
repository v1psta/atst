import pytest
from werkzeug.datastructures import ImmutableMultiDict

from atst.forms.new_request import DetailsOfUseForm


class TestDetailsOfUseForm:

    form_data = {
        "dod_component": "Army and Air Force Exchange Service",
        "jedi_usage": "cloud-ify all the things",
        "num_software_systems": "12",
        "estimated_monthly_spend": "1000000",
        "dollar_value": "42",
        "number_user_sessions": "6",
        "average_daily_traffic": "0",
        "start_date": "12/12/2050",
        "name": "blue-beluga",
    }
    migration_data = {
        "jedi_migration": "yes",
        "rationalization_software_systems": "yes",
        "technical_support_team": "yes",
        "organization_providing_assistance": "In-house staff",
        "engineering_assessment": "yes",
        "data_transfers": "Less than 100GB",
        "expected_completion_date": "Less than 1 month",
    }

    def _make_form(self, data):
        form_data = ImmutableMultiDict(data.items())
        return DetailsOfUseForm(form_data)

    def test_require_cloud_native_when_not_migrating(self):
        extra_data = {"jedi_migration": "no"}
        request_form = self._make_form({**self.form_data, **extra_data})
        assert not request_form.validate()
        assert request_form.errors == {"cloud_native": ["Not a valid choice"]}

    def test_require_migration_questions_when_migrating(self):
        extra_data = {
            "jedi_migration": "yes",
            "data_transfers": "",
            "expected_completion_date": "",
        }
        request_form = self._make_form({**self.form_data, **extra_data})
        assert not request_form.validate()
        assert request_form.errors == {
            "rationalization_software_systems": ["Not a valid choice"],
            "technical_support_team": ["Not a valid choice"],
            "organization_providing_assistance": ["Not a valid choice"],
            "engineering_assessment": ["Not a valid choice"],
            "data_transfers": ["This field is required."],
            "expected_completion_date": ["This field is required."],
        }

    def test_require_organization_when_technical_support_team(self):
        data = {**self.form_data, **self.migration_data}
        del data["organization_providing_assistance"]

        request_form = self._make_form(data)
        assert not request_form.validate()
        assert request_form.errors == {
            "organization_providing_assistance": ["Not a valid choice"]
        }

    def test_valid_form_data(self):
        data = {**self.form_data, **self.migration_data}
        data["technical_support_team"] = "no"
        del data["organization_providing_assistance"]

        request_form = self._make_form(data)
        assert request_form.validate()

    def test_sessions_required_for_large_projects(self):
        data = {**self.form_data, **self.migration_data}
        data["estimated_monthly_spend"] = "9999999"
        del data["number_user_sessions"]
        del data["average_daily_traffic"]

        request_form = self._make_form(data)
        assert not request_form.validate()
        assert request_form.errors == {
            "number_user_sessions": ["This field is required."],
            "average_daily_traffic": ["This field is required."],
        }

    def test_sessions_not_required_low_monthly_spend(self):
        data = {**self.form_data, **self.migration_data}
        data["estimated_monthly_spend"] = "10"
        del data["number_user_sessions"]
        del data["average_daily_traffic"]

        request_form = self._make_form(data)
        assert request_form.validate()

    def test_start_date_must_be_in_the_future(self):
        data = {**self.form_data, **self.migration_data}
        data["start_date"] = "01/01/2018"

        request_form = self._make_form(data)
        assert not request_form.validate()
        assert "Must be a date in the future." in request_form.errors["start_date"]
