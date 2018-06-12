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
    @tornado.gen.coroutine
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.get_cookie('bearer-token'):
                bearer_token = self.get_cookie('bearer-token')
                valid = yield validate_login_token(self.application.authnid_client, bearer_token)
                if valid:
                    self._start_session()
                else:
                    raise NotImplementedError
            elif self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                self.redirect(url)
                return
            else:
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper

@tornado.gen.coroutine
def validate_login_token(client, token):
    try:
        response = yield client.post('/api/v1/validate', raise_error=False, json={"token": token})
        return response.code == 200
    except tornado.httpclient.HTTPError as error:
        if error.response.code == 401:
            return False
        else:
            raise error

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
