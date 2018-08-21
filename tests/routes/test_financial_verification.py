import urllib
from flask import url_for

from atst.eda_client import MockEDAClient

from tests.mocks import MOCK_REQUEST, MOCK_USER
from tests.factories import PENumberFactory, RequestFactory


class TestPENumberInForm:

    required_data = {
        "pe_id": "123",
        "task_order_number": MockEDAClient.MOCK_CONTRACT_NUMBER,
        "fname_co": "Contracting",
        "lname_co": "Officer",
        "email_co": "jane@mail.mil",
        "office_co": "WHS",
        "fname_cor": "Officer",
        "lname_cor": "Representative",
        "email_cor": "jane@mail.mil",
        "office_cor": "WHS",
        "uii_ids": "1234",
        "treasury_code": "00123456",
        "ba_code": "024A"
    }
    extended_data = {
        "funding_type": "RDTE",
        "funding_type_other": "other",
        "clin_0001": "50,000",
        "clin_0003": "13,000",
        "clin_1001": "30,000",
        "clin_1003": "7,000",
        "clin_2001": "30,000",
        "clin_2003": "7,000",
    }

    def _set_monkeypatches(self, monkeypatch):
        monkeypatch.setattr("atst.forms.financial.FinancialForm.validate", lambda s: True)
        monkeypatch.setattr("atst.domain.auth.get_current_user", lambda *args: MOCK_USER)

    def submit_data(self, client, data, extended=False):
        request = RequestFactory.create(body=MOCK_REQUEST.body)
        url_kwargs = {"request_id": request.id}
        if extended:
            url_kwargs["extended"] = True
        response = client.post(
            url_for("requests.financial_verification", **url_kwargs),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=urllib.parse.urlencode(data),
            follow_redirects=False,
        )
        return response

    def test_submit_request_form_with_invalid_pe_id(self, monkeypatch, client):
        self._set_monkeypatches(monkeypatch)

        response = self.submit_data(client, self.required_data)

        assert "We couldn&#39;t find that PE number" in response.data.decode()
        assert response.status_code == 200

    def test_submit_request_form_with_unchanged_pe_id(self, monkeypatch, client):
        self._set_monkeypatches(monkeypatch)

        data = dict(self.required_data)
        data['pe_id'] = MOCK_REQUEST.body['financial_verification']['pe_id']

        response = self.submit_data(client, data)

        assert response.status_code == 302
        assert "/requests/financial_verification_submitted" in response.headers.get("Location")

    def test_submit_request_form_with_new_valid_pe_id(self, monkeypatch, client):
        self._set_monkeypatches(monkeypatch)
        pe = PENumberFactory.create(number="8675309U", description="sample PE number")

        data = dict(self.required_data)
        data['pe_id'] = pe.number

        response = self.submit_data(client, data)

        assert response.status_code == 302
        assert "/requests/financial_verification_submitted" in response.headers.get("Location")

    def test_submit_request_form_with_missing_pe_id(self, monkeypatch, client):
        self._set_monkeypatches(monkeypatch)

        data = dict(self.required_data)
        data['pe_id'] = ''

        response = self.submit_data(client, data)

        assert "There were some errors" in response.data.decode()
        assert response.status_code == 200

    def test_submit_financial_form_with_invalid_task_order(self, monkeypatch, user_session, client):
        monkeypatch.setattr("atst.domain.requests.Requests.get", lambda i: MOCK_REQUEST)
        user_session()

        data = dict(self.required_data)
        data['pe_id'] = MOCK_REQUEST.body['financial_verification']['pe_id']
        data['task_order_number'] = '1234'

        response = self.submit_data(client, data)

        assert "enter TO information manually" in response.data.decode()

    def test_submit_financial_form_with_valid_task_order(self, monkeypatch, user_session, client):
        monkeypatch.setattr("atst.domain.requests.Requests.get", lambda i: MOCK_REQUEST)
        user_session()

        data = dict(self.required_data)
        data['pe_id'] = MOCK_REQUEST.body['financial_verification']['pe_id']
        data['task_order_number'] = MockEDAClient.MOCK_CONTRACT_NUMBER

        response = self.submit_data(client, data)

        assert "enter TO information manually" not in response.data.decode()

    def test_submit_extended_financial_form(self, monkeypatch, user_session, client):
        monkeypatch.setattr("atst.domain.requests.Requests.get", lambda i: MOCK_REQUEST)
        user_session()

        data = { **self.required_data, **self.extended_data }
        data['pe_id'] = MOCK_REQUEST.body['financial_verification']['pe_id']
        data['task_order_number'] = "1234567"

        response = self.submit_data(client, data, extended=True)

        assert response.status_code == 302
        assert "/requests/financial_verification_submitted" in response.headers.get("Location")
