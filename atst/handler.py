import tornado.web
from atst.assets import assets
from atst.sessions import SessionNotFoundError

helpers = {"assets": assets}


class BaseHandler(tornado.web.RequestHandler):
    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        helpers["config"] = self.application.config
        ns.update(helpers)
        return ns

    def login(self, user):
        session_id = self.sessions.start_session(user)
        self.set_secure_cookie("atat", session_id)
        self.redirect("/home")

    def get_current_user(self):
        cookie = self.get_secure_cookie("atat")
        if cookie:
            try:
                session = self.application.sessions.get_session(cookie)
            except SessionNotFoundError:
                self.redirect("/login")
        else:
            return None

        return session["user"]
