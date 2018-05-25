import os
from webassets import Environment, Bundle
import tornado.web
from atst.home import home

class BaseHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        assets = Environment(
                        directory = home.child('scss'),
                        url       = '/static')
        css    = Bundle(
                        'atat.scss',
                        filters = 'scss',
                        output  = '../static/assets/out.css')

        assets.register( 'css', css )
        helpers = {
            'assets': assets
        }

        ns = super(BaseHandler, self).get_template_namespace()
        ns.update(helpers)
        return ns
