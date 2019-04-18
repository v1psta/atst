from flask import Blueprint, request as http_request, g, render_template
from operator import attrgetter

portfolios_bp = Blueprint("portfolios", __name__)

from . import index
from . import applications
from . import members
from . import invitations
from . import task_orders
from atst.domain.exceptions import UnauthorizedError
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.utils.context_processors import portfolio as portfolio_context_processor


portfolios_bp.context_processor(portfolio_context_processor)
