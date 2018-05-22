#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("hello.html.to")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ],
    template_path='./templates',
    debug=os.getenv('DEBUG',False),
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
