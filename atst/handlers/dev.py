import tornado.gen

from atst.handler import BaseHandler


class Dev(BaseHandler):
    def initialize(self, action, sessions, authz_client):
        self.action = action
        self.sessions = sessions
        self.authz_client = authz_client

    @tornado.gen.coroutine
    def get(self):
        user = {
            "id": "164497f6-c1ea-4f42-a5ef-101da278c012",
            "first_name": "Test",
            "last_name": "User",
        }
        yield self.login(user)
