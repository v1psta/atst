import os
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
                output  = '../static/assets/out.%(version)s.css',
                depends = ('**/*.scss'))

assets.register( 'css', css )
helpers = {
    'assets': assets
}

class BaseHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update(helpers)
        return ns
