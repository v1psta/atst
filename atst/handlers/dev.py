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
        user_permissions = yield self.get_or_fetch_user_permissions(user["id"])
        user["atat_permissions"] = user_permissions
        self.login(user)

    @tornado.gen.coroutine
    def get_or_fetch_user_permissions(self, user_id):
        response = yield self.authz_client.post(
            "/users", json={"id": user_id, "atat_role": "ccpo"}, raise_error=False
        )
        if response.code == 200:
            return response.json["atat_permissions"]
        elif response.code == 409:
            # User already exists
            response = yield self.authz_client.get("/users/{}".format(user_id))
            return response.json["atat_permissions"]
