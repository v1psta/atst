from flask import Blueprint, current_app as app, g, redirect, url_for

applications_bp = Blueprint("applications", __name__)

from . import index
from . import new
from . import settings
from . import invitations
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import UnauthorizedError
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.utils.context_processors import portfolio as portfolio_context_processor

applications_bp.context_processor(portfolio_context_processor)


def wrap_environment_role_lookup(user, environment_id=None, **kwargs):
    env_role = EnvironmentRoles.get_by_user_and_environment(user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(user, "access environment {}".format(environment_id))

    return True


@applications_bp.route("/environments/<environment_id>/access")
@user_can(None, override=wrap_environment_role_lookup, message="access environment")
def access_environment(environment_id):
    env_role = EnvironmentRoles.get_by_user_and_environment(
        g.current_user.id, environment_id
    )
    login_url = app.csp.cloud.get_environment_login_url(env_role.environment)

    return redirect(url_for("atst.csp_environment_access", login_url=login_url))
