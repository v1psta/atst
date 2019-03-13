import urllib.parse as url
from flask import (
    Blueprint,
    render_template,
    g,
    redirect,
    session,
    url_for,
    request,
    make_response,
)

from flask import current_app as app
from jinja2.exceptions import TemplateNotFound
import pendulum
import os
from werkzeug.exceptions import NotFound

from atst.domain.users import Users
from atst.domain.authnid import AuthenticationContext
from atst.domain.audit_log import AuditLog
from atst.domain.auth import logout as _logout
from atst.domain.common import Paginator
from atst.domain.portfolios import Portfolios
from atst.utils.flash import formatted_flash as flash


bp = Blueprint("atst", __name__)


@bp.route("/")
def root():
    if g.current_user:
        return redirect(url_for(".home"))

    redirect_url = app.config.get("CAC_URL")
    if request.args.get("next"):
        redirect_url = url.urljoin(
            redirect_url,
            "?{}".format(url.urlencode({"next": request.args.get("next")})),
        )
        flash("login_next")

    return render_template("login.html", redirect_url=redirect_url)


@bp.route("/help")
@bp.route("/help/<path:doc>")
def helpdocs(doc=None):
    docs = [os.path.splitext(file)[0] for file in os.listdir("templates/help/docs")]
    if doc:
        return render_template("help/docs/{}.html".format(doc), docs=docs, doc=doc)
    else:
        return render_template("help/index.html", docs=docs, doc=doc)


@bp.route("/home")
def home():
    user = g.current_user
    num_portfolios = len([role for role in user.portfolio_roles if role.is_active])

    if num_portfolios == 0:
        return redirect(url_for("portfolios.portfolios"))
    elif num_portfolios == 1:
        portfolio_role = user.portfolio_roles[0]
        portfolio_id = portfolio_role.portfolio.id
        is_portfolio_owner = "portfolio_poc" in [
            ps.name for ps in portfolio_role.permission_sets
        ]

        if is_portfolio_owner:
            return redirect(
                url_for("portfolios.portfolio_reports", portfolio_id=portfolio_id)
            )
        else:
            return redirect(
                url_for("portfolios.portfolio_applications", portfolio_id=portfolio_id)
            )
    else:
        portfolios = Portfolios.for_user(g.current_user)
        first_portfolio = sorted(portfolios, key=lambda portfolio: portfolio.name)[0]
        return redirect(
            url_for(
                "portfolios.portfolio_applications", portfolio_id=first_portfolio.id
            )
        )


@bp.route("/styleguide")
def styleguide():
    return render_template("styleguide.html")


@bp.route("/<path:path>")
def catch_all(path):
    try:
        return render_template("{}.html".format(path))
    except TemplateNotFound:
        raise NotFound()


def _make_authentication_context():
    return AuthenticationContext(
        crl_cache=app.crl_cache,
        auth_status=request.environ.get("HTTP_X_SSL_CLIENT_VERIFY"),
        sdn=request.environ.get("HTTP_X_SSL_CLIENT_S_DN"),
        cert=request.environ.get("HTTP_X_SSL_CLIENT_CERT"),
    )


def redirect_after_login_url():
    if request.args.get("next"):
        returl = request.args.get("next")
        if request.args.get(app.form_cache.PARAM_NAME):
            returl += "?" + url.urlencode(
                {app.form_cache.PARAM_NAME: request.args.get(app.form_cache.PARAM_NAME)}
            )
        return returl
    else:
        return url_for("atst.home")


@bp.route("/login-redirect")
def login_redirect():
    auth_context = _make_authentication_context()
    auth_context.authenticate()
    user = auth_context.get_user()

    if user.provisional:
        Users.finalize(user)

    session["user_id"] = user.id

    return redirect(redirect_after_login_url())


@bp.route("/logout")
def logout():
    _logout()
    response = make_response(redirect(url_for(".root")))
    response.set_cookie("expandSidenav", "", expires=0)
    return response


@bp.route("/activity-history")
def activity_history():
    pagination_opts = Paginator.get_pagination_opts(request)
    audit_events = AuditLog.get_all_events(g.current_user, pagination_opts)
    return render_template("audit_log/audit_log.html", audit_events=audit_events)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/csp-environment-access")
def csp_environment_access():
    return render_template("mock_csp.html", text="console for this environment")


@bp.route("/jedi-csp-calculator")
def jedi_csp_calculator():
    return redirect(app.csp.cloud.calculator_url())
