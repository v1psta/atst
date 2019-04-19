from flask import Blueprint, current_app as app, g, redirect, url_for

applications_bp = Blueprint("applications", __name__)

from . import index
from . import new
from . import settings
from . import team
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.exceptions import UnauthorizedError
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.permissions import Permissions
from atst.utils.context_processors import portfolio as portfolio_context_processor

applications_bp.context_processor(portfolio_context_processor)


def wrap_environment_role_lookup(user, environment_id=None, **kwargs):
    env_role = EnvironmentRoles.get(user.id, environment_id)
    if not env_role:
        raise UnauthorizedError(user, "access environment {}".format(environment_id))

    return True


@applications_bp.route("/environments/<environment_id>/access")
@user_can(None, override=wrap_environment_role_lookup, message="access environment")
def access_environment(environment_id):
    env_role = EnvironmentRoles.get(g.current_user.id, environment_id)
    token = app.csp.cloud.get_access_token(env_role)

    return redirect(url_for("atst.csp_environment_access", token=token))
