import os
import functools
from webassets import Environment, Bundle
import tornado.web
from atst.home import home

# module variables used by the handlers

assets = Environment(
                directory = home.child('scss'),
                url       = '/static')
css    = Bundle(
                'atat.scss',
                filters = 'scss',
                output  = '../static/assets/out.css',
                depends = ('**/*.scss'))

assets.register( 'css', css )
helpers = {
    'assets': assets
}

def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                self.redirect(url)
                return
            else:
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update(helpers)
        return ns

    def get_current_user(self):
        if self.get_secure_cookie('atst'):
            return True
        else:
            False

    # this is a temporary implementation until we have real sessions
    def _start_session(self):
        self.set_secure_cookie('atst', 'valid-user-session')
