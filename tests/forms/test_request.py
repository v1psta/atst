import pytest

from atst.forms.request import RequestForm


class TestRequestForm:

    form_data = {
        'dod_component': 'us_air_force',
        'jedi_usage': 'cloud-ify all the things',
        'num_software_systems': '12',
        'estimated_monthly_spend': '34',
        'dollar_value': '42',
        'number_user_sessions': '6',
        'average_daily_traffic': '0',
        'start_date': '12/12/2012',
    }

    def test_require_cloud_native_when_not_migrating(self):
        extra_data = { 'jedi_migration': 'no' }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert not request_form.validate()
        assert request_form.errors == { 'cloud_native': ['Not a valid choice'] }

    def test_require_migration_questions_when_migrating(self):
        extra_data = { 'jedi_migration': 'yes' }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert not request_form.validate()
        assert request_form.errors == {
            'rationalization_software_systems': ['Not a valid choice'],
            'technical_support_team': ['Not a valid choice'],
            'organization_providing_assistance': ['Not a valid choice'],
            'engineering_assessment': ['Not a valid choice'],
            'data_transfers': ['Not a valid choice'],
            'expected_completion_date': ['Not a valid choice']
        }

    def test_require_organization_when_technical_support_team(self):
        extra_data = {
            'jedi_migration': 'yes',
            'rationalization_software_systems': 'yes',
            'technical_support_team': 'yes',
            'engineering_assessment': 'yes',
            'data_transfers': 'less_than_100gb',
            'expected_completion_date': 'less_than_1_month'
        }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert not request_form.validate()
        assert request_form.errors == {
            'organization_providing_assistance': ['Not a valid choice'],
        }

    def test_valid_form_data(self):
        extra_data = {
            'jedi_migration': 'yes',
            'rationalization_software_systems': 'yes',
            'technical_support_team': 'no',
            'engineering_assessment': 'yes',
            'data_transfers': 'less_than_100gb',
            'expected_completion_date': 'less_than_1_month'
        }
        request_form = RequestForm(data={ **self.form_data, **extra_data })
        assert request_form.validate()
