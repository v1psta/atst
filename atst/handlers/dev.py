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
    "admin": {
        "id": "66ebf7b8-cbf0-4ed8-a102-5f105330df75",
        "first_name": "Andreas",
        "last_name": "Admin",
    },
    "developer": {
        "id": "7707b9f2-5945-49ae-967a-be65baa88baf",
        "first_name": "Dominick",
        "last_name": "Developer",
    },
    "billing_auditor": {
        "id": "6978ac0c-442a-46aa-a0c3-ff17b5ec2a8c",
        "first_name": "Billie",
        "last_name": "The Billing Auditor",
    },
    "security_auditor": {
        "id": "596fd001-bb1d-4adf-87d8-fa2312e882de",
        "first_name": "Sawyer",
        "last_name": "The Security Auditor",
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
        yield self._set_user_permissions(user["id"], role)
        yield self.login(user)

    @tornado.gen.coroutine
    def _set_user_permissions(self, user_id, role):
        response = yield self.authz_client.post(
            "/users", json={"id": user_id, "atat_role": role}
        )
        return response.json
