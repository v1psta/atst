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
        self.redirect("/requests")
