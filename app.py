#!/usr/bin/env python

from atst.app import make_app
import tornado.ioloop
import os

app = make_app(debug=os.getenv('DEBUG',False))
port = 8888
app.listen(port)
print("Listening on http://localhost:%i" % port)
tornado.ioloop.IOLoop.current().start()
