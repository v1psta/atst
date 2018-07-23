import tornado
from collections import defaultdict

from atst.handler import BaseHandler
from atst.forms.request import RequestForm
from atst.forms.org import OrgForm
from atst.forms.poc import POCForm
from atst.forms.review import ReviewForm
from atst.forms.financial import FinancialForm


class RequestFinancialVerification(BaseHandler):
    def initialize(self, page, requests_client, fundz_client):
        self.page = page
        self.requests_client = requests_client
        self.fundz_client = fundz_client

    @tornado.gen.coroutine
    def get_existing_request(self, request_id):
        if request_id is None:
            return {}
        request = yield self.requests_client.get("/requests/{}".format(request_id))
        return request.json

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, request_id=None):
        # self.check_xsrf_cookie()
        # post_data = self.request.arguments
        current_user = self.get_current_user()
        existing_request = yield self.get_existing_request(request_id)
        self.render(
            "requests/financial_verification.html.to",
            page=self.page,
        )

