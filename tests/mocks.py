import tornado.gen
from tornado.httpclient import HTTPRequest, HTTPResponse

from atst.api_client import ApiClient
from tests.factories import RequestFactory, UserFactory


MOCK_USER = UserFactory.create()
MOCK_REQUEST = RequestFactory.create(
    creator=MOCK_USER.id,
    body={
        "financial_verification": {
            "pe_id": "0203752A",
        },
    }
)
DOD_SDN_INFO = {
        'first_name': 'ART',
        'last_name': 'GARFUNKEL',
        'dod_id': '5892460358'
    }
DOD_SDN = f"CN={DOD_SDN_INFO['last_name']}.{DOD_SDN_INFO['first_name']}.G.{DOD_SDN_INFO['dod_id']},OU=OTHER,OU=PKI,OU=DoD,O=U.S. Government,C=US"


class MockApiClient(ApiClient):

    def __init__(self, service):
        self.service = service

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return self._get_response("GET", path)

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return self._get_response("PUT", path)

    @tornado.gen.coroutine
    def patch(self, path, **kwargs):
        return self._get_response("PATCH", path)

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return self._get_response("POST", path)

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return self._get_response("DELETE", path)

    def _get_response(self, verb, path, code=200, json=None):
        response = HTTPResponse(
            request=HTTPRequest(path, verb),
            code=code,
            headers={"Content-Type": "application/json"},
        )

        setattr(response, "ok", 200 <= code < 300)
        if json:
            setattr(response, "json", json)

        return response


MOCK_VALID_PE_ID = "8675309U"
