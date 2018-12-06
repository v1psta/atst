import urllib.parse as url
from flask import Blueprint, render_template, g, redirect, session, url_for, request

from flask import current_app as app
from jinja2.exceptions import TemplateNotFound
import pendulum
import os

from atst.domain.requests import Requests
from atst.domain.users import Users
from atst.domain.authnid import AuthenticationContext
from atst.domain.audit_log import AuditLog
from atst.domain.auth import logout as _logout
from werkzeug.exceptions import NotFound


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

    return render_template(
        "login.html", redirect=bool(request.args.get("next")), redirect_url=redirect_url
    )


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

    if user.atat_role_name == "ccpo":
        return redirect(url_for("requests.requests_index"))

    num_workspaces = len(user.workspace_roles)

    if num_workspaces == 0:
        return redirect(url_for("requests.requests_index"))
    elif num_workspaces == 1:
        workspace_role = user.workspace_roles[0]
        workspace_id = workspace_role.workspace.id
        is_request_owner = workspace_role.role.name == "owner"

        if is_request_owner:
            return redirect(
                url_for("workspaces.workspace_reports", workspace_id=workspace_id)
            )
        else:
            return redirect(
                url_for("workspaces.workspace_projects", workspace_id=workspace_id)
            )
    else:
        return redirect(url_for("workspaces.workspaces"))


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
    return redirect(url_for(".root"))


def get_pagination_opts(request, default_page=1, default_per_page=100):
    return {
        "page": int(request.args.get("page", default_page)),
        "per_page": int(request.args.get("perPage", default_per_page)),
    }


@bp.route("/activity-history")
def activity_history():
    pagination_opts = get_pagination_opts(request)
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
    return render_template("mock_csp.html", text="service and price calculator")


import secrets
from atst.forms.edit_user import EditUserForm
from atst.utils.docx import Docx


@bp.route("/docx", methods=["GET", "POST"])
def docx():
    filename = None
    if request.method == "POST":
        app.logger.info(request.form)
        bytes_ = Docx.render(
            character=request.form.get("character"), vehicle=request.form.get("vehicle")
        )
        filename = "{}.docx".format(secrets.token_urlsafe(16))
        with open(
            os.path.join(app.root_path, "..", "static", "docx_demo", filename), "wb"
        ) as docx:
            docx.write(bytes_)

    form = EditUserForm()
    return render_template("docx_demo.html", f=form, docx=filename)
