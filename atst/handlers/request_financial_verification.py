import tornado

from atst.handler import BaseHandler
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
        existing_request = yield self.get_existing_request(request_id)
        form = FinancialForm(data=existing_request['body'].get('financial_verification'))
        self.render(
            "requests/financial_verification.html.to",
            page=self.page,
            f=form,
            request_id=request_id,
        )

    @tornado.gen.coroutine
    def update_request(self, request_id, form_data):
        request_data = {
            "creator_id": self.current_user["id"],
            "request": {"financial_verification": form_data},
        }
        response = yield self.requests_client.patch(
            "/requests/{}".format(request_id), json=request_data
        )
        return response

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, request_id=None):
        self.check_xsrf_cookie()
        post_data = self.request.arguments
        existing_request = yield self.get_existing_request(request_id)
        form = FinancialForm(post_data)

        rerender_args = dict(request_id=request_id, f=form)

        if form.validate():
            response = yield self.update_request(request_id, form.data)
            if response.ok:
                valid = yield form.perform_extra_validation(
                    existing_request.get('body', {}).get('financial_verification'),
                    self.fundz_client
                )
                if valid:
                    self.redirect('/requests')
                else:
                    self.render(
                        "requests/financial_verification.html.to",
                        **rerender_args
                    )
            else:
                self.set_status(response.code)
        else:
            self.render(
                "requests/financial_verification.html.to",
                **rerender_args
            )
