import os
from configparser import ConfigParser
import tornado.web
from tornado.web import url
from redis import StrictRedis

from flask import Flask

from atst.handlers.main import Main
from atst.handlers.root import Root
from atst.handlers.login_redirect import LoginRedirect
from atst.handlers.workspaces import Workspaces
from atst.handlers.workspace import Workspace
from atst.handlers.workspace_members import WorkspaceMembers
from atst.handlers.request import Request
from atst.handlers.request_financial_verification import RequestFinancialVerification
from atst.handlers.request_new import RequestNew
from atst.handlers.request_submit import RequestsSubmit
from atst.handlers.dev import Dev
from atst.home import home
from atst.api_client import ApiClient
from atst.sessions import RedisSessions
from atst import ui_modules
from atst import ui_methods

from atst.database import db

ENV = os.getenv("TORNADO_ENV", "dev")

def make_app(config):
    app = Flask(__name__)
    app.config.update(config)

    db.init_app(app)

    return app


# def make_app(config, deps, **kwargs):

#     routes = [
#         url(r"/", Root, {"page": "root"}, name="root"),
#         url(
#             r"/login-redirect",
#             LoginRedirect,
#             {
#                 "sessions": deps["sessions"],
#                 "authnid_client": deps["authnid_client"],
#                 "db_session": deps["db_session"],
#             },
#             name="login_redirect",
#         ),
#         url(r"/home", Main, {"page": "home"}, name="home"),
#         url(r"/styleguide", Main, {"page": "styleguide"}, name="styleguide"),
#         url(
#             r"/workspaces/blank",
#             Main,
#             {"page": "workspaces_blank"},
#             name="workspaces_blank",
#         ),
#         url(
#             r"/workspaces",
#             Workspaces,
#             {"page": "workspaces", "db_session": deps["db_session"]},
#             name="workspaces",
#         ),
#         url(
#             r"/requests",
#             Request,
#             {"page": "requests", "db_session": deps["db_session"]},
#             name="requests",
#         ),
#         url(
#             r"/requests/new",
#             RequestNew,
#             {
#                 "page": "requests_new",
#                 "db_session": deps["db_session"],
#             },
#             name="request_new",
#         ),
#         url(
#             r"/requests/new/([0-9])",
#             RequestNew,
#             {
#                 "page": "requests_new",
#                 "db_session": deps["db_session"],
#             },
#             name="request_form_new",
#         ),
#         url(
#             r"/requests/new/([0-9])/(\S+)",
#             RequestNew,
#             {
#                 "page": "requests_new",
#                 "db_session": deps["db_session"],
#             },
#             name="request_form_update",
#         ),
#         url(
#             r"/requests/submit/(\S+)",
#             RequestsSubmit,
#             {"db_session": deps["db_session"]},
#             name="requests_submit",
#         ),
#         # Dummy request/approval screen
#         url(
#             r"/request/approval",
#             Main,
#             {"page": "request_approval"},
#             name="request_approval",
#         ),
#         url(
#             r"/requests/verify/(\S+)",
#             RequestFinancialVerification,
#             {
#                 "page": "financial_verification",
#                 "db_session": deps["db_session"],
#             },
#             name="financial_verification",
#         ),
#         url(
#             r"/requests/financial_verification_submitted",
#             Main,
#             {"page": "requests/financial_verification_submitted"},
#             name="financial_verification_submitted",
#         ),
#         url(r"/users", Main, {"page": "users"}, name="users"),
#         url(r"/reports", Main, {"page": "reports"}, name="reports"),
#         url(r"/calculator", Main, {"page": "calculator"}, name="calculator"),
#         url(
#             r"/workspaces/(\S+)/members", WorkspaceMembers, {}, name="workspace_members"
#         ),
#         url(r"/workspaces/(\S+)/projects", Workspace, {}, name="workspace_projects"),
#     ]

#     if not ENV == "production":
#         routes += [
#             url(
#                 r"/login-dev",
#                 Dev,
#                 {
#                     "action": "login",
#                     "sessions": deps["sessions"],
#                     "db_session": deps["db_session"],
#                 },
#                 name="dev-login",
#             )
#         ]

#     app = tornado.web.Application(
#         routes,
#         login_url="/",
#         template_path=home.child("templates"),
#         static_path=home.child("static"),
#         cookie_secret=config["default"]["COOKIE_SECRET"],
#         debug=config["default"].getboolean("DEBUG"),
#         ui_modules=ui_modules,
#         ui_methods=ui_methods,
#         **kwargs
#     )
#     app.config = config
#     app.sessions = deps["sessions"]
#     return app


# def make_deps(config):
#     # we do not want to do SSL verify services in test and development
#     validate_cert = ENV == "production"
#     redis_client = StrictRedis.from_url(
#         config["default"]["REDIS_URI"], decode_responses=True
#     )

def make_config():
    BASE_CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "../config/base.ini")
    ENV_CONFIG_FILENAME = os.path.join(
        os.path.dirname(__file__),
        "../config/",
        "{}.ini".format(os.getenv("FLASK_ENV", "dev").lower()),
    )
    config = ConfigParser()

    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read([BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME])

    # Assemble DATABASE_URI value
    database_uri = (
        "postgres://"
        + config.get("default", "DATABASE_USERNAME")
        + ":"
        + config.get("default", "DATABASE_PASSWORD")
        + "@"
        + config.get("default", "DATABASE_HOST")
        + ":"
        + config.get("default", "DATABASE_PORT")
        + "/"
        + config.get("default", "DATABASE_NAME")
    )
    config.set("default", "DATABASE_URI", database_uri)

    return map_config(config)


def map_config(config):
    return {
        "ENV": config["default"]["ENVIRONMENT"],
        "DEBUG": config["default"]["DEBUG"],
        "PORT": int(config["default"]["PORT"]),
        "SQLALCHEMY_DATABASE_URI": config["default"]["DATABASE_URI"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
