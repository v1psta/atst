import tornado.gen

from atst.handler import BaseHandler

_DEV_USERS = {
    "ccpo": {
        "id": "164497f6-c1ea-4f42-a5ef-101da278c012",
        "first_name": "Sam",
        "last_name": "CCPO",
    },
    "owner": {
        "id": "cce17030-4109-4719-b958-ed109dbb87c8",
        "first_name": "Olivia",
        "last_name": "Owner",
    },
}


class Dev(BaseHandler):

    def initialize(self, action, sessions, authz_client):
        self.action = action
        self.sessions = sessions
        self.authz_client = authz_client

    @tornado.gen.coroutine
    def get(self):
        role = self.get_argument("role", "ccpo")
        user = _DEV_USERS[role]
        yield self.login(user)
