import os
from configparser import ConfigParser
import tornado.web
from tornado.web import url

from atst.handlers.main import MainHandler
from atst.handlers.home import Home
from atst.handlers.login import Login
from atst.handlers.workspace import Workspace
from atst.handlers.request import Request
from atst.handlers.request_new import RequestNew
from atst.handlers.dev import Dev
from atst.home import home
from atst.api_client import ApiClient

ENV = os.getenv("TORNADO_ENV", "dev")


def make_app(config):

    authz_client = ApiClient(config["default"]["AUTHZ_BASE_URL"])
    authnid_client = ApiClient(config["default"]["AUTHNID_BASE_URL"])

    routes = [
        url(r"/", Home, {"page": "login"}, name="main"),
        url(
            r"/login",
            Login,
            {"authnid_client": authnid_client},
            name="login",
        ),
        url(r"/home", MainHandler, {"page": "home"}, name="home"),
        url( r"/workspaces/blank",       MainHandler, {'page': 'workspaces_blank'},       name='workspaces_blank' ),
        url(
            r"/workspaces",
            Workspace,
            {"page": "workspaces", "authz_client": authz_client},
            name="workspaces",
        ),
        url(r"/requests", Request, {"page": "requests"}, name="requests"),
        url(r"/requests/new", RequestNew, {"page": "requests_new"}, name="request_new"),
        url(
            r"/requests/new/([0-9])",
            RequestNew,
            {"page": "requests_new"},
            name="request_form",
        ),
        url(r"/users", MainHandler, {"page": "users"}, name="users"),
        url(r"/reports", MainHandler, {"page": "reports"}, name="reports"),
        url(r"/calculator", MainHandler, {"page": "calculator"}, name="calculator"),
    ]

    if not ENV == "production":
        routes += [url(r"/login-dev", Dev, {"action": "login"}, name="dev-login")]

    app = tornado.web.Application(
        routes,
        login_url="/",

        template_path = home.child('templates'),
        static_path   = home.child('static'),
        cookie_secret=config["default"]["COOKIE_SECRET"],
        debug=config['default'].getboolean('DEBUG')
    )
    return app


def make_config():
    BASE_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__),
        "../config/base.ini"
    )
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__),
        "../config/",
        "{}.ini".format(ENV.lower())
    )
    config = ConfigParser()

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read([BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME])
    return config
