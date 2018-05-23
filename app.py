#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import os
from tornado.log import enable_pretty_logging

enable_pretty_logging()

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        self.ssl_verified = self.request.headers.get('X-CLIENT-VERIFY') == 'SUCCESS'
        self.ssl_sdn = self.request.headers.get('X-SSL-ClIENT-S-DN')

    def get(self):
        self.render("hello.html.to", sdn=self.ssl_sdn, verified=self.ssl_verified)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ],
    debug=os.getenv('DEBUG',False),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Listening on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
