import tornado.web
from atst.assets import environment
from atst.sessions import SessionNotFoundError

helpers = {"assets": environment}


class BaseHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        helpers["config"] = self.application.config
        ns.update(helpers)
        return ns

    @tornado.gen.coroutine
    def login(self, user):
        user["atat_permissions"] = yield self._get_user_permissions(user["id"])
        session_id = self.sessions.start_session(user)
        self.set_secure_cookie("atat", session_id)
        return self.redirect("/home")

    @tornado.gen.coroutine
    def _get_user_permissions(self, user_id):
        response = yield self.authz_client.post(
            "/users", json={"id": user_id, "atat_role": "ccpo"}
        )
        return response.json["atat_permissions"]

    def get_current_user(self):
        cookie = self.get_secure_cookie("atat")
        if cookie:
            try:
                session = self.application.sessions.get_session(cookie)
            except SessionNotFoundError:
                return None

        else:
            return None

        return session["user"]
