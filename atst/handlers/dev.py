import tornado.gen

from atst.handler import BaseHandler

_DEV_USERS = {
    "sam": {
        "id": "164497f6-c1ea-4f42-a5ef-101da278c012",
        "first_name": "Sam",
        "last_name": "CCPO",
        "atat_role": "ccpo"
    },

    "amanda": {
        "id": "cce17030-4109-4719-b958-ed109dbb87c8",
        "first_name": "Amanda",
        "last_name": "Adamson",
        "atat_role": "default"
    },
    "brandon": {
        "id": "66ebf7b8-cbf0-4ed8-a102-5f105330df75",
        "first_name": "Brandon",
        "last_name": "Buchannan",
        "atat_role": "default"
    },
    "christina": {
        "id": "7707b9f2-5945-49ae-967a-be65baa88baf",
        "first_name": "Christina",
        "last_name": "Collins",
        "atat_role": "default"
    },
    "dominick": {
        "id": "6978ac0c-442a-46aa-a0c3-ff17b5ec2a8c",
        "first_name": "Dominick",
        "last_name": "Domingo",
        "atat_role": "default"
    },
    "erica": {
        "id": "596fd001-bb1d-4adf-87d8-fa2312e882de",
        "first_name": "Erica",
        "last_name": "Eichner",
        "atat_role": "default"
    },
}

class Dev(BaseHandler):

    def initialize(self, action, sessions, authz_client):
        self.action = action
        self.sessions = sessions
        self.authz_client = authz_client

    @tornado.gen.coroutine
    def get(self):
        role = self.get_argument("username", "amanda")
        user = _DEV_USERS[role]
        yield self._set_user_permissions(user["id"], user["atat_role"])
        yield self.login(user)

    @tornado.gen.coroutine
    def _set_user_permissions(self, user_id, role):
        response = yield self.authz_client.post(
            "/users", json={"id": user_id, "atat_role": role}
        )
        return response.json
