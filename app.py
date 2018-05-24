#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import os
from webassets import Environment, Bundle

# Set up assets.
static_path = os.path.join(os.path.dirname(__file__), "static")
scss_path = os.path.join(os.path.dirname(__file__), "scss")
assets = Environment(directory=scss_path, url='/static')
css = Bundle('atat.scss', output='assets/out.css')
assets.register('css', css)
helpers = {
    'assets': assets
}

class MainHandler(tornado.web.RequestHandler):

    def get_template_namespace(self):
        ns = super(MainHandler, self).get_template_namespace()
        ns.update(helpers)
        return ns

    def get(self):
        self.render("hello.html.to")

def make_app():
    app  = tornado.web.Application([
        (r"/", MainHandler),
    ],
    debug=os.getenv('DEBUG',False),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=static_path
    )
    return app

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Listening on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
