import tornado.web
from atst.handlers.main import MainHandler
from atst.home import home

def make_app(**kwargs):
    app = tornado.web.Application([
            (r"/", MainHandler),
        ],
        template_path = home.child('templates'),
        static_path   = home.child('static'),
        **kwargs
    )
    return app
