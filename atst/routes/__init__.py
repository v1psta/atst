from flask import Blueprint, render_template, g, redirect, session, url_for, request
import pendulum

from atst.domain.requests import Requests
from atst.domain.users import Users
from atst.domain.authnid.utils import parse_sdn

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


@bp.route('/login-redirect')
def log_in_user():
    # FIXME: Find or create user based on the X-Ssl-Client-S-Dn header
    # TODO: Store/log the X-Ssl-Client-Cert in case it's needed?
    if request.environ.get('HTTP_X_SSL_CLIENT_VERIFY') == 'SUCCESS' and is_valid_certificate(request):
        sdn = request.environ.get('HTTP_X_SSL_CLIENT_S_DN')
        # TODO: error handling for bad SDN, database errors, etc
        sdn_parts = parse_sdn(sdn)
        user = Users.get_or_create_by_dod_id(**sdn_parts)

        session["user_id"] = user.id

        return redirect(url_for("atst.home"))
    else:
        template = render_template('not_authorized.html', atst_url=app.config['ATST_PASSTHROUGH'])
        response = app.make_response(template)
        response.status_code = 403

    return response

def is_valid_certificate(request):
    cert = request.environ.get('HTTP_X_SSL_CLIENT_CERT')
    if cert:
        result = app.crl_validator.validate(cert.encode())
        if not result:
            app.logger.info(app.crl_validator.errors[-1])
        return result
    else:
        return False

def construct_redirect(uuid):
    access_token = app.token_manager.token(uuid)
    url = f'{app.config["ATST_REDIRECT"]}?bearer-token={access_token}'
    return app.make_response(redirect(url))
