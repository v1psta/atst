from flask import Blueprint, render_template, g, redirect, session, url_for, request
from flask import current_app as app
import pendulum

from atst.domain.requests import Requests
from atst.domain.users import Users
from atst.domain.authnid.utils import parse_sdn
from atst.domain.exceptions import UnauthenticatedError

bp = Blueprint("atst", __name__)


@bp.route("/")
def root():
    return render_template("root.html")


@bp.route("/home")
def home():
    return render_template("home.html")


@bp.route("/styleguide")
def styleguide():
    return render_template("styleguide.html")


@bp.route('/<path:path>')
def catch_all(path):
    return render_template("{}.html".format(path))


# TODO: this should be partly consolidated into a domain function that takes
# all the necessary UWSGI environment values as args and either returns a user
# or raises the UnauthenticatedError
@bp.route('/login-redirect')
def login_redirect():
    if request.environ.get('HTTP_X_SSL_CLIENT_VERIFY') == 'SUCCESS' and _is_valid_certificate(request):
        sdn = request.environ.get('HTTP_X_SSL_CLIENT_S_DN')
        sdn_parts = parse_sdn(sdn)
        user = Users.get_or_create_by_dod_id(**sdn_parts)
        session["user_id"] = user.id

        return redirect(url_for("atst.home"))
    else:
        raise UnauthenticatedError()


def _is_valid_certificate(request):
    cert = request.environ.get('HTTP_X_SSL_CLIENT_CERT')
    if cert:
        result = app.crl_validator.validate(cert.encode())
        if not result:
            app.logger.info(app.crl_validator.errors[-1])
        return result
    else:
        return False
