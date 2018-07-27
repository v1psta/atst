import tornado

from atst.handler import BaseHandler


class RequestsSubmit(BaseHandler):
    def initialize(self, requests_client):
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, request_id):
        yield self.requests_client.post(
            "/requests/{}/submit".format(request_id),
            allow_nonstandard_methods=True
        )
        approved = yield self._check_approved(request_id)
        if approved:
            self.redirect("/requests?modal=True")
        else:
            self.redirect("/requests")

    @tornado.gen.coroutine
    def _check_approved(self, request_id):
        response = yield self.requests_client.get(
            "/requests/{}".format(request_id)
        )
        status = response.json.get("status")
        return status == "approved"
